import functools
import hashlib
import pickle
import redis

class CacheHook:
    def __init__(self, host='localhost', port=6379, db=0, password=None):
        self.redis_client = redis.Redis(host=host, port=port, db=db, password=password)

    def default_cache_key(self, func, args, kwargs):
        """Generate a default cache key based on function module, name, and arguments."""
        key_raw = f"{func.__module__}.{func.__name__}:{args}:{kwargs}"
        return hashlib.sha256(key_raw.encode()).hexdigest()

    def cache_hook(self, expire=3600, cache_key_func=None):
        """
        Decorator to add Redis cache to a function (e.g., crewai task/flow).
        Checks cache before execution, stores result after execution.
        Args:
            expire (int): Cache expiration time in seconds.
            cache_key_func (callable): Function to generate cache key.
        """
        cache_key_func = cache_key_func or self.default_cache_key
        def decorator(func):
            @functools.wraps(func)
            def wrapper(*args, **kwargs):
                cache_key = cache_key_func(func, args, kwargs)
                cached = self.redis_client.get(cache_key)
                if cached is not None:
                    return pickle.loads(cached)
                result = func(*args, **kwargs)
                self.redis_client.setex(cache_key, expire, pickle.dumps(result))
                return result
            return wrapper
        return decorator

# Singleton usage example
cache = CacheHook()
cache_hook = cache.cache_hook
