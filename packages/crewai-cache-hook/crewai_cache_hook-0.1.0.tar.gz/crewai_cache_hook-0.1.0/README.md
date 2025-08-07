# crewai-cache-hook

A Redis-based cache decorator for crewai tasks or flows.

## Features
- Add cache capability to functions/tasks via a decorator
- Checks Redis cache before execution, returns cached result if hit
- Automatically writes result to Redis cache after execution
- Supports custom cache key, expiration time, and Redis connection parameters

## Installation

```bash
pip install redis
```

## Quick Start

1. Copy `cache_hook.py` to your project directory
2. Use the decorator in your crewai task/flow

```python
from cache_hook import cache_hook

@cache_hook(expire=600)  # Cache for 10 minutes
def my_task(x, y):
    # Your task logic
    return x + y
```

## Advanced Usage

To customize Redis connection parameters:

```python
from cache_hook import CacheHook

my_cache = CacheHook(host='127.0.0.1', port=6379, db=0)
cache_hook = my_cache.cache_hook

@cache_hook(expire=120)
def another_task(a, b):
    ...
```

## Parameters
- `expire`: Cache expiration time (seconds)
- `cache_key_func`: Custom function to generate cache key (optional)
- `host`/`port`/`db`/`password`: Redis connection parameters

## Notes
- Uses pickle for result serialization by default. Ensure your result objects are pickle-serializable.
- Suitable for crewai tasks, flows, or regular Python functions.
