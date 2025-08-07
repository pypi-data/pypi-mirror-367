import functools
import hashlib
import pickle
import redis
import inspect
import logging
import json
from typing import Callable, Any, Optional

class RedisCacheError(Exception):
    """Custom exception for Redis cache-related errors."""
    pass

class CacheHook:
    def __init__(self, host='localhost', port=6379, db=0, password=None, 
                 connect_timeout=2, max_retries=1, 
                 serializer='pickle', compression=False):
        """
        Initialize Redis cache hook with advanced configuration.
        
        Args:
            host (str): Redis server host
            port (int): Redis server port
            db (int): Redis database number
            password (str, optional): Redis password
            connect_timeout (int): Connection timeout in seconds
            max_retries (int): Number of connection retry attempts
            serializer (str): Serialization method ('pickle' or 'json')
            compression (bool): Enable result compression
        """
        self.host = host
        self.port = port
        self.db = db
        self.password = password
        self.connect_timeout = connect_timeout
        self.max_retries = max_retries
        self.serializer = serializer
        self.compression = compression
        
        self.logger = logging.getLogger(__name__)
        self.logger.setLevel(logging.INFO)
        
        self._create_redis_client()

    def _create_redis_client(self):
        """Create a Redis client with retry mechanism."""
        for attempt in range(self.max_retries + 1):
            try:
                self.redis_client = redis.Redis(
                    host=self.host, 
                    port=self.port, 
                    db=self.db, 
                    password=self.password,
                    socket_connect_timeout=self.connect_timeout
                )
                # Perform a quick connection check
                self.redis_client.ping()
                self.logger.info(f"Connected to Redis at {self.host}:{self.port}")
                return
            except (redis.ConnectionError, redis.TimeoutError) as e:
                if attempt < self.max_retries:
                    self.logger.warning(f"Redis connection attempt {attempt + 1} failed: {e}")
                else:
                    raise RedisCacheError(f"Could not connect to Redis after {self.max_retries + 1} attempts") from e

    def _serialize(self, data: Any) -> bytes:
        """
        Serialize data based on selected serializer.
        
        Args:
            data (Any): Data to serialize
        
        Returns:
            bytes: Serialized data
        """
        try:
            if self.serializer == 'json':
                serialized = json.dumps(data).encode('utf-8')
            else:  # default to pickle
                serialized = pickle.dumps(data)
            
            # Optional compression could be added here
            return serialized
        except Exception as e:
            self.logger.error(f"Serialization error: {e}")
            raise

    def _deserialize(self, data: bytes) -> Any:
        """
        Deserialize data based on selected serializer.
        
        Args:
            data (bytes): Data to deserialize
        
        Returns:
            Any: Deserialized data
        """
        try:
            if self.serializer == 'json':
                return json.loads(data.decode('utf-8'))
            else:  # default to pickle
                return pickle.loads(data)
        except Exception as e:
            self.logger.error(f"Deserialization error: {e}")
            raise

    def default_cache_key(self, func: Callable, args: tuple, kwargs: dict) -> str:
        """
        Generate a default cache key based on function details.
        
        Args:
            func (Callable): The function being cached
            args (tuple): Positional arguments
            kwargs (dict): Keyword arguments
        
        Returns:
            str: Generated cache key
        """
        # 处理可能的 self 参数
        if len(args) > 0 and (inspect.ismethod(func) or hasattr(args[0], func.__name__)):
            args = args[1:]
        
        # 创建更详细的缓存键
        key_parts = [
            func.__module__,
            func.__name__,
            str(args),
            str(sorted(kwargs.items()))
        ]
        key_raw = ":".join(key_parts)
        return hashlib.sha256(key_raw.encode()).hexdigest()

    def cache_hook(self, 
                   expire: int = 3600, 
                   cache_key_func: Optional[Callable] = None, 
                   force_refresh: bool = False):
        """
        Decorator to add Redis cache to a task.
        
        Args:
            expire (int): Cache expiration time in seconds
            cache_key_func (callable, optional): Custom function to generate cache key
            force_refresh (bool): Force bypass cache and refresh
        
        Returns:
            Decorator for caching task results
        """
        cache_key_func = cache_key_func or self.default_cache_key
        
        def decorator(func):
            @functools.wraps(func)
            def wrapper(*args, **kwargs):
                try:
                    # Generate cache key
                    cache_key = cache_key_func(func, args, kwargs)
                    
                    # Check force refresh
                    if force_refresh:
                        self.logger.info(f"Force refresh for key: {cache_key}")
                        result = func(*args, **kwargs)
                        self._store_in_cache(cache_key, result, expire)
                        return result
                    
                    # Try to get cached result
                    cached = self.redis_client.get(cache_key)
                    if cached is not None:
                        try:
                            result = self._deserialize(cached)
                            self.logger.info(f"Cache hit for key: {cache_key}")
                            return result
                        except Exception as e:
                            self.logger.warning(f"Cache deserialization failed: {e}")
                    
                    # Execute original function
                    result = func(*args, **kwargs)
                    
                    # Cache the result
                    self._store_in_cache(cache_key, result, expire)
                    
                    return result
                
                except RedisCacheError as e:
                    # If Redis connection fails, fall back to original function
                    self.logger.warning(f"Redis cache unavailable: {e}. Executing without cache.")
                    return func(*args, **kwargs)
                
                except Exception as e:
                    # Handle any unexpected errors
                    self.logger.error(f"Unexpected error in cache hook: {e}")
                    return func(*args, **kwargs)
            
            return wrapper
        return decorator

    def _store_in_cache(self, cache_key: str, result: Any, expire: int):
        """
        Store result in Redis cache.
        
        Args:
            cache_key (str): Cache key
            result (Any): Result to cache
            expire (int): Expiration time
        """
        try:
            serialized_result = self._serialize(result)
            self.redis_client.setex(cache_key, expire, serialized_result)
            self.logger.info(f"Cached result for key: {cache_key}")
        except Exception as storage_error:
            self.logger.error(f"Cache storage error: {storage_error}")

# Singleton usage
cache = CacheHook()
cache_hook = cache.cache_hook
