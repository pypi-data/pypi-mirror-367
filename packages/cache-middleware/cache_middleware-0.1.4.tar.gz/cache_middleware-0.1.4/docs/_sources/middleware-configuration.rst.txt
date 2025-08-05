Middleware Configuration
========================

This section provides detailed information about configuring the Cache Middleware, including backend options, decorator parameters, and advanced settings.

Backend Configuration
---------------------

Cache Backend Interface
~~~~~~~~~~~~~~~~~~~~~~~~

All cache backends implement the ``CacheBackend`` interface:

.. code-block:: python

   from abc import ABC, abstractmethod
   from typing import Optional

   class CacheBackend(ABC):
       """Abstract base class for cache backends."""
       
       @abstractmethod
       async def get(self, key: str) -> Optional[str]:
           """Get a value from the cache."""
           pass
       
       @abstractmethod
       async def set(self, key: str, value: str, timeout: int) -> None:
           """Set a value in the cache with expiration."""
           pass
       
       @abstractmethod
       async def delete(self, key: str) -> None:
           """Delete a key from the cache."""
           pass
       
       @abstractmethod
       async def close(self) -> None:
           """Close backend connections."""
           pass

Redis Backend Options
~~~~~~~~~~~~~~~~~~~~~

The ``RedisBackend`` supports extensive configuration:

.. code-block:: python

   from cache_middleware.backends.redis_backend import RedisBackend

   redis_backend = RedisBackend(
       url="redis://localhost:6379",           # Redis connection URL
       max_connections=10,                     # Max connections in pool
       retry_on_timeout=True,                  # Retry on timeout
       socket_keepalive=True,                  # Enable TCP keepalive
       socket_keepalive_options={              # TCP keepalive settings
           1: 1,  # TCP_KEEPIDLE
           2: 3,  # TCP_KEEPINTVL
           3: 5,  # TCP_KEEPCNT
       },
       health_check_interval=30,               # Health check interval (seconds)
       password=None,                          # Redis password
       db=0,                                   # Redis database number
       encoding='utf-8',                       # String encoding
       decode_responses=True,                  # Auto-decode responses
       socket_timeout=5.0,                     # Socket timeout
       socket_connect_timeout=5.0,             # Connection timeout
       connection_pool=None,                   # Custom connection pool
       ssl=False,                              # Enable SSL
       ssl_keyfile=None,                       # SSL key file
       ssl_certfile=None,                      # SSL certificate file
       ssl_cert_reqs='required',               # SSL certificate requirements
       ssl_ca_certs=None,                      # SSL CA certificates
       ssl_check_hostname=False,               # Verify hostname in SSL
       max_connections_per_pool=50,            # Max connections per pool
   )

**URL Format Examples:**

.. code-block:: python

   # Basic Redis
   "redis://localhost:6379"
   
   # Redis with password
   "redis://:password@localhost:6379"
   
   # Redis with username and password
   "redis://username:password@localhost:6379"
   
   # Redis with specific database
   "redis://localhost:6379/1"
   
   # Redis with SSL
   "rediss://localhost:6380"
   
   # Redis Sentinel
   "redis+sentinel://sentinel-host:26379/mymaster"

**Production Redis Configuration:**

.. code-block:: python

   redis_backend = RedisBackend(
       url="redis://prod-redis-01:6379",
       max_connections=50,
       retry_on_timeout=True,
       socket_keepalive=True,
       health_check_interval=30,
       socket_timeout=10.0,
       socket_connect_timeout=10.0,
       # Enable SSL for production
       ssl=True,
       ssl_cert_reqs='required',
       ssl_ca_certs='/etc/ssl/certs/redis-ca.pem'
   )

Memory Backend Options
~~~~~~~~~~~~~~~~~~~~~~

The ``MemoryBackend`` has simpler configuration:

.. code-block:: python

   from cache_middleware.backends.memory_backend import MemoryBackend

   memory_backend = MemoryBackend(
       max_size=1000,          # Maximum number of cached items
       cleanup_interval=300,    # Cleanup expired items every 5 minutes
       default_timeout=3600,    # Default timeout for items (1 hour)
   )

**Memory Usage Considerations:**

- Each cached item stores both key and value in memory
- Large response bodies consume significant memory
- Consider using Redis for production or large datasets
- Monitor memory usage in production environments

Custom Backend Configuration
~~~~~~~~~~~~~~~~~~~~~~~~~~~~

For implementing custom backends:

.. code-block:: python

   from cache_middleware.backends.base import CacheBackend

   class CustomBackend(CacheBackend):
       def __init__(self, custom_param: str, timeout: int = 300):
           self.custom_param = custom_param
           self.default_timeout = timeout
           self.storage = {}

       async def get(self, key: str) -> Optional[str]:
           item = self.storage.get(key)
           if item and item['expires'] > time.time():
               return item['value']
           elif item:
               del self.storage[key]  # Clean up expired item
           return None

       async def set(self, key: str, value: str, timeout: int) -> None:
           expires = time.time() + timeout
           self.storage[key] = {'value': value, 'expires': expires}

       async def delete(self, key: str) -> None:
           self.storage.pop(key, None)

       async def close(self) -> None:
           self.storage.clear()

Decorator Configuration
-----------------------

Cache Decorator Options
~~~~~~~~~~~~~~~~~~~~~~~

The ``@cache`` decorator accepts several parameters:

.. code-block:: python

   from cache_middleware.decorators import cache

   @cache(
       timeout=300,            # Cache timeout in seconds
       cache_control=True,     # Respect HTTP Cache-Control headers
       exclude_headers=None,   # Headers to exclude from cache key
       include_headers=None,   # Headers to include in cache key
   )
   async def my_endpoint():
       return {"data": "cached"}

**Timeout Configuration:**

.. code-block:: python

   # Short-lived cache (1 minute)
   @cache(timeout=60)
   async def real_time_data():
       return {"timestamp": time.time()}

   # Medium-lived cache (5 minutes)
   @cache(timeout=300)
   async def user_profile(user_id: int):
       return {"user_id": user_id}

   # Long-lived cache (1 hour)
   @cache(timeout=3600)
   async def application_config():
       return {"version": "1.0"}

**Cache-Control Header Support:**

.. code-block:: python

   @cache(timeout=300, cache_control=True)
   async def cacheable_endpoint():
       """
       Supports standard HTTP Cache-Control directives:
       - no-cache: Bypasses cache for this request
       - no-store: Prevents caching of this response
       - max-age=60: Overrides default timeout
       """
       return {"data": "value"}

**Header-Based Cache Keys:**

.. code-block:: python

   # Include specific headers in cache key
   @cache(timeout=300, include_headers=['Accept-Language', 'User-Agent'])
   async def localized_content():
       return {"message": "Hello"}

   # Exclude sensitive headers from cache key
   @cache(timeout=300, exclude_headers=['Authorization', 'Cookie'])
   async def public_data():
       return {"public": "data"}

Middleware Registration
-----------------------

Basic Registration
~~~~~~~~~~~~~~~~~~

Register the middleware with your FastAPI application:

.. code-block:: python

   from fastapi import FastAPI
   from cache_middleware.middleware import CacheMiddleware
   from cache_middleware.backends.redis_backend import RedisBackend

   app = FastAPI()

   # Create backend instance
   backend = RedisBackend(url="redis://localhost:6379")

   # Register middleware
   app.add_middleware(CacheMiddleware, backend=backend)

**Important Notes:**

- Backend must be fully initialized before passing to middleware
- Middleware should be registered before route definitions
- Each application instance requires its own backend instance

Middleware with Dependency Injection
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

For advanced scenarios, use dependency injection:

.. code-block:: python

   from fastapi import FastAPI, Depends
   from cache_middleware.helpers import get_cache_backend

   app = FastAPI()

   async def get_backend():
       """Dependency to provide cache backend"""
       return get_cache_backend()

   # Use in routes that need direct cache access
   @app.get("/cache-stats")
   async def cache_stats(backend: CacheBackend = Depends(get_backend)):
       # Direct backend access for administrative functions
       return {"status": "operational"}

Multiple Middleware Instances
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

For applications needing different cache strategies:

.. code-block:: python

   # Different backends for different purposes
   session_backend = RedisBackend(url="redis://localhost:6379/0")
   data_backend = RedisBackend(url="redis://localhost:6379/1")

   # Register multiple middleware instances (not recommended)
   # Instead, use a single middleware with smart routing

   # Better approach: Backend router
   class BackendRouter(CacheBackend):
       def __init__(self, backends: dict):
           self.backends = backends

       async def get(self, key: str) -> Optional[str]:
           backend_name = self._get_backend_for_key(key)
           return await self.backends[backend_name].get(key)

       def _get_backend_for_key(self, key: str) -> str:
           if key.startswith("session:"):
               return "session"
           return "data"

Environment-Based Configuration
-------------------------------

Development Configuration
~~~~~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: python

   import os
   from cache_middleware.helpers import create_backend_from_env

   def get_development_backend():
       """Development-specific backend configuration"""
       if os.getenv("USE_REDIS", "false").lower() == "true":
           return RedisBackend(
               url=os.getenv("REDIS_URL", "redis://localhost:6379"),
               max_connections=5  # Lower connection pool for dev
           )
       else:
           return MemoryBackend(max_size=100)  # Small cache for dev

Production Configuration
~~~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: python

   def get_production_backend():
       """Production-specific backend configuration"""
       return RedisBackend(
           url=os.getenv("REDIS_URL"),
           max_connections=int(os.getenv("REDIS_MAX_CONNECTIONS", "50")),
           retry_on_timeout=True,
           socket_keepalive=True,
           health_check_interval=30,
           socket_timeout=10.0,
           # Production SSL settings
           ssl=os.getenv("REDIS_SSL", "false").lower() == "true",
           ssl_cert_reqs='required',
           ssl_ca_certs=os.getenv("REDIS_SSL_CA_CERTS"),
       )

Configuration Factory
~~~~~~~~~~~~~~~~~~~~~

Create a configuration factory for different environments:

.. code-block:: python

   class CacheConfig:
       @staticmethod
       def create_backend(environment: str) -> CacheBackend:
           config_map = {
               "development": CacheConfig._development_config,
               "testing": CacheConfig._testing_config,
               "staging": CacheConfig._staging_config,
               "production": CacheConfig._production_config,
           }
           
           config_func = config_map.get(environment)
           if not config_func:
               raise ValueError(f"Unknown environment: {environment}")
           
           return config_func()

       @staticmethod
       def _development_config() -> CacheBackend:
           return MemoryBackend(max_size=100)

       @staticmethod
       def _testing_config() -> CacheBackend:
           return MemoryBackend(max_size=50)

       @staticmethod
       def _staging_config() -> CacheBackend:
           return RedisBackend(
               url=os.getenv("REDIS_URL", "redis://staging-redis:6379"),
               max_connections=10
           )

       @staticmethod
       def _production_config() -> CacheBackend:
           return RedisBackend(
               url=os.getenv("REDIS_URL"),
               max_connections=50,
               retry_on_timeout=True,
               socket_keepalive=True,
               ssl=True
           )

Cache Key Configuration
-----------------------

Default Key Generation
~~~~~~~~~~~~~~~~~~~~~~

The middleware generates cache keys using this pattern:

.. code-block:: python

   # Key format: cache:{hash}
   # Hash includes: method, path, query parameters, request body
   
   def generate_cache_key(request):
       method = request.method
       path = request.url.path
       query_params = sorted(request.url.query.split("&"))
       body = await request.body()
       
       key_base = f"{method}:{path}?{'&'.join(query_params)}|{body.decode()}"
       cache_key = f"cache:{hashlib.sha256(key_base.encode()).hexdigest()}"
       return cache_key

Custom Key Generation
~~~~~~~~~~~~~~~~~~~~~

Override key generation for specific needs:

.. code-block:: python

   class CustomCacheMiddleware(CacheMiddleware):
       def generate_cache_key(self, request):
           # Custom key generation logic
           user_id = request.headers.get("X-User-ID", "anonymous")
           endpoint = request.url.path
           return f"user_cache:{user_id}:{endpoint}"

Cache Invalidation
~~~~~~~~~~~~~~~~~~

Implement cache invalidation patterns:

.. code-block:: python

   @app.post("/invalidate-cache")
   async def invalidate_cache(pattern: str, backend: CacheBackend = Depends(get_backend)):
       """Invalidate cache entries matching pattern"""
       if hasattr(backend, 'delete_pattern'):
           await backend.delete_pattern(pattern)
       return {"message": "Cache invalidated"}

   # Tag-based invalidation
   @cache(timeout=300, tags=["user_data", f"user_{user_id}"])
   async def get_user_profile(user_id: int):
       return {"user_id": user_id}

Performance Tuning
-------------------

Connection Pooling
~~~~~~~~~~~~~~~~~~

Optimize Redis connection pooling:

.. code-block:: python

   # High-traffic configuration
   redis_backend = RedisBackend(
       url="redis://localhost:6379",
       max_connections=100,  # Increased pool size
       socket_keepalive=True,
       socket_keepalive_options={
           1: 600,  # TCP_KEEPIDLE (10 minutes)
           2: 60,   # TCP_KEEPINTVL (1 minute)
           3: 3,    # TCP_KEEPCNT
       },
       health_check_interval=60,
       socket_timeout=30.0,
   )

Memory Optimization
~~~~~~~~~~~~~~~~~~~

For memory-constrained environments:

.. code-block:: python

   # Optimize memory backend
   memory_backend = MemoryBackend(
       max_size=500,           # Smaller cache size
       cleanup_interval=60,    # More frequent cleanup
   )

   # Use compression for large responses
   class CompressedMemoryBackend(MemoryBackend):
       async def set(self, key: str, value: str, timeout: int) -> None:
           compressed_value = gzip.compress(value.encode())
           await super().set(key, compressed_value, timeout)

       async def get(self, key: str) -> Optional[str]:
           compressed_value = await super().get(key)
           if compressed_value:
               return gzip.decompress(compressed_value).decode()
           return None

Monitoring Configuration
------------------------

Logging Configuration
~~~~~~~~~~~~~~~~~~~~~

Configure detailed cache monitoring:

.. code-block:: python

   from cache_middleware.logger_config import configure_logger, logger
   
   # Production logging
   configure_logger()
   logger.add(
       "cache_middleware.log",
       rotation="100 MB",
       retention="30 days",
       level="INFO",
       format="{time:YYYY-MM-DD HH:mm:ss} | {level} | {message}",
       serialize=True  # JSON format for log aggregation
   )

Metrics Collection
~~~~~~~~~~~~~~~~~~

Integrate with monitoring systems:

.. code-block:: python

   class MetricsBackend(CacheBackend):
       def __init__(self, backend: CacheBackend, metrics_client):
           self.backend = backend
           self.metrics = metrics_client

       async def get(self, key: str) -> Optional[str]:
           start_time = time.time()
           result = await self.backend.get(key)
           duration = time.time() - start_time
           
           self.metrics.histogram('cache.get.duration', duration)
           self.metrics.increment('cache.get.requests')
           
           if result:
               self.metrics.increment('cache.get.hits')
           else:
               self.metrics.increment('cache.get.misses')
           
           return result

Health Checks
~~~~~~~~~~~~~

Implement backend health monitoring:

.. code-block:: python

   @app.get("/health/cache")
   async def cache_health(backend: CacheBackend = Depends(get_backend)):
       """Check cache backend health"""
       try:
           # Test cache operations
           test_key = f"health_check_{int(time.time())}"
           await backend.set(test_key, "ok", 10)
           result = await backend.get(test_key)
           await backend.delete(test_key)
           
           if result == "ok":
               return {"status": "healthy", "backend": type(backend).__name__}
           else:
               return {"status": "degraded", "error": "Cache not responding correctly"}
       except Exception as e:
           return {"status": "unhealthy", "error": str(e)}

Next Steps
----------

- Learn how to implement custom backends in :doc:`extending-backends`
- Check the complete API documentation in :doc:`api`
- Return to practical examples in :doc:`user-guide`
