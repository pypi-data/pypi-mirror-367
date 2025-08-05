#!/usr/bin/env python3
"""
Example of how to configure different cache backends with dependency injection
"""

from fastapi import Body, FastAPI
from cache_middleware.middleware import CacheMiddleware
from cache_middleware.decorators import cache

# Optional imports with error handling
try:
    from cache_middleware.backends.redis_backend import RedisBackend
    _REDIS_AVAILABLE = True
except ImportError:
    _REDIS_AVAILABLE = False
    print("Warning: Redis backend not available. Install with: pip install cache-middleware[redis]")

from cache_middleware.backends.memory_backend import MemoryBackend


def create_app_with_redis():
    """Application with Redis backend"""
    if not _REDIS_AVAILABLE:
        raise ImportError(
            "Redis backend requires 'redis[hiredis]'. "
            "Install with: pip install cache-middleware[redis]"
        )
    
    app = FastAPI(title="Cache App - Redis")
    
    # Create and configure Redis backend
    redis_backend = RedisBackend(
        url="redis://localhost:6379",
        max_connections=20
    )
    
    app.add_middleware(CacheMiddleware, backend=redis_backend)
    return app


def create_app_with_memory():
    """Application with memory backend"""
    app = FastAPI(title="Cache App - Memory")
    
    # Create and configure memory backend
    memory_backend = MemoryBackend(max_size=1000)
    
    app.add_middleware(CacheMiddleware, backend=memory_backend)
    return app


def create_app_with_custom_backend():
    """Application with custom backend"""
    from cache_middleware.backends import CacheBackend
    from cache_middleware.logger_config import logger
    import asyncio
    import time
    from typing import Optional
    
    class CustomBackend(CacheBackend):
        """Custom backend that combines memory and logs"""
        
        def __init__(self):
            self.memory_cache = {}
            logger.info("Custom backend initialized")
        
        async def get(self, key: str) -> Optional[str]:
            logger.info(f"Getting key: {key}")
            return self.memory_cache.get(key)
        
        async def set(self, key: str, value: str, timeout: int) -> None:
            logger.info(f"Setting key: {key} with timeout: {timeout}")
            self.memory_cache[key] = value
            
            # Simulate expiration after timeout
            async def expire_key():
                await asyncio.sleep(timeout)
                self.memory_cache.pop(key, None)
                logger.info(f"Key expired: {key}")
            
            # Create background task to expire the key
            asyncio.create_task(expire_key())
        
        async def delete(self, key: str) -> None:
            logger.info(f"Deleting key: {key}")
            self.memory_cache.pop(key, None)
        
        async def close(self) -> None:
            logger.info("Custom backend closed")
            self.memory_cache.clear()
    
    app = FastAPI(title="Cache App - Custom")
    custom_backend = CustomBackend()
    app.add_middleware(CacheMiddleware, backend=custom_backend)
    return app


def create_app_with_hybrid_backend():
    """Hybrid backend that uses memory + Redis"""
    if not _REDIS_AVAILABLE:
        raise ImportError(
            "Hybrid backend requires Redis. "
            "Install with: pip install cache-middleware[redis]"
        )
    
    from cache_middleware.backends import CacheBackend
    from typing import Optional
    
    class HybridBackend(CacheBackend):
        """Backend that combines local memory with remote Redis"""
        
        def __init__(self, memory_backend: MemoryBackend, redis_backend):
            self.memory = memory_backend
            self.redis = redis_backend
        
        async def get(self, key: str) -> Optional[str]:
            # First search in memory (faster)
            result = await self.memory.get(key)
            if result:
                return result
            
            # If not in memory, search in Redis
            result = await self.redis.get(key)
            if result:
                # Save in memory for next access (local cache)
                await self.memory.set(key, result, 60)  # 1 minute in memory
            
            return result
        
        async def set(self, key: str, value: str, timeout: int) -> None:
            # Save in both backends
            await self.memory.set(key, value, min(timeout, 60))  # Maximum 1 min in memory
            await self.redis.set(key, value, timeout)
        
        async def delete(self, key: str) -> None:
            await self.memory.delete(key)
            await self.redis.delete(key)
        
        async def close(self) -> None:
            await self.memory.close()
            await self.redis.close()
    
    app = FastAPI(title="Cache App - Hybrid")
    
    # Create individual backends
    memory_backend = MemoryBackend(max_size=100)
    redis_backend = RedisBackend(url="redis://localhost:6379")
    
    # Create hybrid backend
    hybrid_backend = HybridBackend(memory_backend, redis_backend)
    
    app.add_middleware(CacheMiddleware, backend=hybrid_backend)
    return app


# Example endpoints for any app
@cache(timeout=300)
async def get_items(q: str = None, page: int = 1):
    return {"query": q, "page": page, "result": [f"item-{i}" for i in range(1, 6)]}


@cache(timeout=120) 
async def get_user(user_id: int):
    return {"id": user_id, "name": f"User {user_id}", "email": f"user{user_id}@example.com"}


@cache(timeout=120)
async def calculate(data: dict = Body(...)):
    """
    Calculate the sum of numbers with caching.
    
    This endpoint demonstrates caching for POST requests with body content.
    The cache key includes the request body to ensure different inputs
    are cached separately.
    
    Parameters
    ----------
    data : dict
        Dictionary containing a 'numbers' key with a list of numbers
        
    Returns
    -------
    dict
        Dictionary with the original input and the calculated sum
    """
    # Simulate expensive operation
    result = sum(data.get("numbers", []))
    return {"input": data, "sum": result}




def setup_app_routes(app: FastAPI):
    """Add example routes to any app"""
    app.add_api_route("/items", get_items, methods=["GET"])
    app.add_api_route("/users/{user_id}", get_user, methods=["GET"])
    app.add_api_route("/calculate", calculate, methods=["POST"])



if __name__ == "__main__":
    import uvicorn
    
    # Build available apps based on installed dependencies
    apps = {
        "memory": create_app_with_memory,
        "custom": create_app_with_custom_backend
    }
    
    # Add Redis-dependent apps only if Redis is available
    if _REDIS_AVAILABLE:
        apps["redis"] = create_app_with_redis
        apps["hybrid"] = create_app_with_hybrid_backend
    
    # Change to the backend type you want to test
    app_type = "memory"  # memory, custom, redis (if available), hybrid (if available)
    
    if app_type not in apps:
        available_types = list(apps.keys())
        raise ValueError(f"Backend '{app_type}' not available. Available: {available_types}")
    
    # Create the selected app
    app = apps[app_type]()
    
    # Add endpoints
    setup_app_routes(app)
    
    print(f"Available backends: {list(apps.keys())}")
    print(f"Using backend: {app_type}")
    print("Starting server at http://localhost:8000")
    print("Test: http://localhost:8000/items?q=test&page=1")
    
    uvicorn.run(app, host="0.0.0.0", port=8000)

