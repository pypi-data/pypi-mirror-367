import pytest
import redis
import json
import pickle
import logging
from unittest.mock import Mock, patch

# 导入待测试的模块
from cache_hook import CacheHook, RedisCacheError

# 配置日志
logging.basicConfig(level=logging.INFO)

class TestCacheHook:
    @pytest.fixture
    def mock_redis(self):
        """创建模拟的 Redis 客户端"""
        with patch('redis.Redis') as mock_redis_class:
            mock_redis_instance = Mock()
            mock_redis_class.return_value = mock_redis_instance
            yield mock_redis_instance

    def test_default_initialization(self, mock_redis):
        """测试默认初始化参数"""
        mock_redis.ping.return_value = True
        cache_hook = CacheHook()
        
        assert cache_hook.host == 'localhost'
        assert cache_hook.port == 6379
        assert cache_hook.db == 0
        assert cache_hook.serializer == 'pickle'
        assert cache_hook.compression is False

    def test_custom_initialization(self, mock_redis):
        """测试自定义初始化参数"""
        mock_redis.ping.return_value = True
        cache_hook = CacheHook(
            host='redis.test.com', 
            port=6380, 
            db=1, 
            password='secret', 
            serializer='json'
        )
        
        assert cache_hook.host == 'redis.test.com'
        assert cache_hook.port == 6380
        assert cache_hook.db == 1
        assert cache_hook.serializer == 'json'

    def test_serialization_pickle(self):
        """测试 Pickle 序列化"""
        cache_hook = CacheHook(serializer='pickle')
        test_data = {'key': 'value', 'number': 42}
        
        serialized = cache_hook._serialize(test_data)
        deserialized = cache_hook._deserialize(serialized)
        
        assert deserialized == test_data

    def test_serialization_json(self):
        """测试 JSON 序列化"""
        cache_hook = CacheHook(serializer='json')
        test_data = {'key': 'value', 'number': 42}
        
        serialized = cache_hook._serialize(test_data)
        deserialized = cache_hook._deserialize(serialized)
        
        assert deserialized == test_data

    def test_cache_key_generation(self):
        """测试缓存键生成"""
        def test_func(x, y):
            return x + y
        
        cache_hook = CacheHook()
        key1 = cache_hook.default_cache_key(test_func, (1, 2), {})
        key2 = cache_hook.default_cache_key(test_func, (1, 2), {})
        key3 = cache_hook.default_cache_key(test_func, (2, 1), {})
        
        assert key1 == key2  # 相同参数应生成相同键
        assert key1 != key3  # 不同参数应生成不同键

    def test_cache_hook_decorator(self, mock_redis):
        """测试缓存装饰器基本功能"""
        mock_redis.ping.return_value = True
        mock_redis.get.return_value = None
        
        cache_hook = CacheHook()
        
        @cache_hook.cache_hook(expire=600)
        def test_func(x, y):
            return x + y
        
        # 第一次调用，应该执行函数并缓存
        result1 = test_func(1, 2)
        mock_redis.setex.assert_called_once()
        
        # 重置 mock
        mock_redis.get.return_value = pickle.dumps(result1)
        
        # 第二次调用，应该返回缓存结果
        result2 = test_func(1, 2)
        assert result1 == result2

    def test_force_refresh(self, mock_redis):
        """测试强制刷新功能"""
        mock_redis.ping.return_value = True
        mock_redis.get.return_value = None
        
        cache_hook = CacheHook()
        
        @cache_hook.cache_hook(expire=600, force_refresh=True)
        def test_func(x, y):
            return x + y
        
        result1 = test_func(1, 2)
        mock_redis.setex.assert_called_once()  # 总是会缓存
        
        # 再次调用，仍然会执行并缓存
        result2 = test_func(1, 2)
        assert result1 == result2

    def test_custom_cache_key(self, mock_redis):
        """测试自定义缓存键生成器"""
        mock_redis.ping.return_value = True
        mock_redis.get.return_value = None
        
        cache_hook = CacheHook()
        
        def custom_key_generator(func, args, kwargs):
            return f"custom:{args[0]}:{args[1]}"
        
        @cache_hook.cache_hook(expire=600, cache_key_func=custom_key_generator)
        def test_func(x, y):
            return x + y
        
        result1 = test_func(1, 2)
        mock_redis.setex.assert_called_once()
        
        # 检查是否使用了自定义键生成器
        assert "custom:1:2" in str(mock_redis.setex.call_args[0][0])

    def test_connection_failure(self):
        """测试 Redis 连接失败"""
        with patch('redis.Redis') as mock_redis_class:
            mock_redis_class.side_effect = redis.ConnectionError("Connection failed")
            
            with pytest.raises(RedisCacheError):
                CacheHook(max_retries=0)

    def test_serialization_error(self, mock_redis):
        """测试序列化错误处理"""
        mock_redis.ping.return_value = True
        mock_redis.get.return_value = b'invalid_data'
        
        cache_hook = CacheHook()
        
        @cache_hook.cache_hook(expire=600)
        def test_func(x, y):
            return x + y
        
        # 模拟反序列化失败
        result = test_func(1, 2)
        assert result == 3  # 应该回退到原始函数

# 如果直接运行此文件，执行测试
if __name__ == '__main__':
    pytest.main([__file__])
