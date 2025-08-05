API Reference
=============

This section provides detailed API documentation for all modules, classes, and functions in the Cache Middleware package.

Core Components
---------------

.. automodule:: cache_middleware.middleware
   :members:
   :undoc-members:
   :show-inheritance:

.. automodule:: cache_middleware.decorators
   :members:
   :undoc-members:
   :show-inheritance:

Backend Implementations
-----------------------

Redis Backend
~~~~~~~~~~~~~

.. automodule:: cache_middleware.backends.redis_backend
   :members:
   :undoc-members:
   :show-inheritance:

Memory Backend
~~~~~~~~~~~~~~

.. automodule:: cache_middleware.backends.memory_backend
   :members:
   :undoc-members:
   :show-inheritance:

Helper Functions
----------------

.. automodule:: cache_middleware.helpers
   :members:
   :undoc-members:
   :show-inheritance:

Logger Configuration
--------------------

.. automodule:: cache_middleware.logger_config
   :members:
   :undoc-members:
   :show-inheritance:

Type Definitions
----------------

The Cache Middleware uses type hints throughout the codebase. Here are the key types:

.. code-block:: python

   from typing import Optional, Any, Dict, List, Union, Callable
   from starlette.requests import Request
   from starlette.responses import Response

   # Cache backend type hint
   CacheBackendType = CacheBackend

   # Cache decorator type hint
   CacheDecoratorType = Callable[[Callable], Callable]

   # Request/Response types from Starlette
   RequestType = Request
   ResponseType = Response

   # Configuration types
   CacheConfigType = Dict[str, Any]
   BackendConfigType = Dict[str, Union[str, int, bool]]

Class Hierarchy
---------------

Backend Classes
~~~~~~~~~~~~~~~

.. code-block:: text

   CacheBackend (ABC)
   ├── MemoryBackend
   ├── RedisBackend
   └── Custom backends (user-defined)

Middleware Classes
~~~~~~~~~~~~~~~~~~

.. code-block:: text

   BaseHTTPMiddleware
   └── CacheMiddleware

Exception Classes
~~~~~~~~~~~~~~~~~

.. code-block:: text

   Exception
   ├── CacheMiddlewareError (future)
   │   ├── BackendError (future)
   │   ├── ConfigurationError (future)
   │   └── SerializationError (future)
   └── ValueError (built-in)
       └── InvalidTimeoutError (future)

Usage Examples
--------------

Basic API Usage
~~~~~~~~~~~~~~~

Creating and configuring backends:

.. code-block:: python

   from cache_middleware.backends.redis_backend import RedisBackend
   from cache_middleware.backends.memory_backend import MemoryBackend
   from cache_middleware.middleware import CacheMiddleware
   from cache_middleware.decorators import cache

   # Create Redis backend
   redis_backend = RedisBackend(
       url="redis://localhost:6379",
       max_connections=10
   )

   # Create Memory backend
   memory_backend = MemoryBackend(max_size=1000)

   # Register middleware with FastAPI
   app.add_middleware(CacheMiddleware, backend=redis_backend)

   # Use cache decorator
   @app.get("/data")
   @cache(timeout=300)
   async def get_data():
       return {"data": "cached_response"}

Advanced API Usage
~~~~~~~~~~~~~~~~~~

Custom backend implementation:

.. code-block:: python

   from cache_middleware.backends.base import CacheBackend
   from typing import Optional

   class CustomBackend(CacheBackend):
       async def get(self, key: str) -> Optional[str]:
           # Custom implementation
           pass

       async def set(self, key: str, value: str, timeout: int) -> None:
           # Custom implementation
           pass

       async def delete(self, key: str) -> None:
           # Custom implementation
           pass

       async def close(self) -> None:
           # Custom implementation
           pass

Helper Functions API
~~~~~~~~~~~~~~~~~~~~

Configuration helpers:

.. code-block:: python

   from cache_middleware.helpers import (
       auto_configure_backend,
       get_backend_for_environment,
       create_redis_backend,
       create_memory_backend
   )

   # Auto-configure from environment
   backend = auto_configure_backend()

   # Environment-specific backend
   backend = get_backend_for_environment("production")

   # Direct backend creation
   redis_backend = create_redis_backend(
       url="redis://localhost:6379",
       max_connections=20
   )

Configuration Parameters
------------------------

CacheMiddleware Parameters
~~~~~~~~~~~~~~~~~~~~~~~~~~

.. list-table::
   :header-rows: 1
   :widths: 20 20 60

   * - Parameter
     - Type
     - Description
   * - backend
     - CacheBackend
     - Cache backend instance (required)
   * - exclude_paths
     - List[str]
     - Paths to exclude from caching
   * - include_paths
     - List[str]
     - Only cache these specific paths
   * - cache_header_name
     - str
     - HTTP header for cache status (default: "X-Cache-Status")

@cache Decorator Parameters
~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. list-table::
   :header-rows: 1
   :widths: 20 20 60

   * - Parameter
     - Type
     - Description
   * - timeout
     - int
     - Cache timeout in seconds (required)
   * - cache_control
     - bool
     - Respect HTTP Cache-Control headers (default: True)
   * - exclude_headers
     - List[str]
     - Headers to exclude from cache key
   * - include_headers
     - List[str]
     - Headers to include in cache key
   * - vary_on
     - List[str]
     - Additional parameters for cache key variation

RedisBackend Parameters
~~~~~~~~~~~~~~~~~~~~~~~

.. list-table::
   :header-rows: 1
   :widths: 20 20 60

   * - Parameter
     - Type
     - Description
   * - url
     - str
     - Redis connection URL (required)
   * - max_connections
     - int
     - Maximum connections in pool (default: 10)
   * - retry_on_timeout
     - bool
     - Retry operations on timeout (default: True)
   * - socket_keepalive
     - bool
     - Enable TCP keepalive (default: True)
   * - socket_keepalive_options
     - Dict[int, int]
     - TCP keepalive options
   * - health_check_interval
     - int
     - Health check interval in seconds (default: 30)
   * - password
     - str
     - Redis password (optional)
   * - db
     - int
     - Redis database number (default: 0)
   * - ssl
     - bool
     - Enable SSL connection (default: False)
   * - ssl_keyfile
     - str
     - SSL key file path
   * - ssl_certfile
     - str
     - SSL certificate file path
   * - ssl_cert_reqs
     - str
     - SSL certificate requirements
   * - ssl_ca_certs
     - str
     - SSL CA certificates file path

MemoryBackend Parameters
~~~~~~~~~~~~~~~~~~~~~~~~

.. list-table::
   :header-rows: 1
   :widths: 20 20 60

   * - Parameter
     - Type
     - Description
   * - max_size
     - int
     - Maximum number of cached items (default: 1000)
   * - cleanup_interval
     - int
     - Cleanup interval in seconds (default: 300)
   * - default_timeout
     - int
     - Default timeout for items (default: 3600)

Environment Variables
---------------------

The Cache Middleware supports configuration via environment variables:

.. list-table::
   :header-rows: 1
   :widths: 30 70

   * - Variable
     - Description
   * - CACHE_BACKEND
     - Backend type: "redis" or "memory"
   * - REDIS_URL
     - Redis connection URL
   * - REDIS_MAX_CONNECTIONS
     - Maximum Redis connections
   * - REDIS_PASSWORD
     - Redis password
   * - REDIS_DB
     - Redis database number
   * - REDIS_SSL
     - Enable Redis SSL ("true"/"false")
   * - MEMORY_CACHE_SIZE
     - Memory backend max size
   * - CACHE_DEFAULT_TIMEOUT
     - Default cache timeout in seconds
   * - CACHE_CLEANUP_INTERVAL
     - Cleanup interval in seconds

Error Handling
--------------

The Cache Middleware provides built-in error handling. Custom exception classes will be implemented in future versions:

- **CacheMiddlewareError**: Base exception for all cache-related errors
- **BackendError**: Raised when backend operations fail
- **ConfigurationError**: Raised for invalid configuration
- **SerializationError**: Raised when response serialization fails

Error Codes
~~~~~~~~~~~

.. list-table::
   :header-rows: 1
   :widths: 20 80

   * - Code
     - Description
   * - BACKEND_ERROR
     - Backend operation failed
   * - CONFIGURATION_ERROR
     - Invalid configuration provided
   * - SERIALIZATION_ERROR
     - Failed to serialize/deserialize response
   * - TIMEOUT_ERROR
     - Operation timed out
   * - CONNECTION_ERROR
     - Failed to connect to backend service

HTTP Headers
------------

Cache Status Headers
~~~~~~~~~~~~~~~~~~~~

The middleware adds cache status information via HTTP headers:

.. list-table::
   :header-rows: 1
   :widths: 30 70

   * - Header
     - Description
   * - X-Cache-Status
     - "HIT" or "MISS" indicating cache status
   * - X-Cache-Key
     - The cache key used (debug mode only)
   * - X-Cache-Timeout
     - Cache timeout value used
   * - X-Cache-Backend
     - Backend type used for caching

Request Headers
~~~~~~~~~~~~~~~

Headers that affect caching behavior:

.. list-table::
   :header-rows: 1
   :widths: 30 70

   * - Header
     - Description
   * - Cache-Control
     - Standard HTTP cache control directives
   * - If-None-Match
     - ETag validation (future feature)
   * - Pragma
     - HTTP/1.0 cache control (no-cache support)

Cache-Control Directives
~~~~~~~~~~~~~~~~~~~~~~~~

Supported Cache-Control directives:

.. list-table::
   :header-rows: 1
   :widths: 30 70

   * - Directive
     - Description
   * - no-cache
     - Bypass cache for this request
   * - no-store
     - Do not cache this response
   * - max-age=seconds
     - Override default cache timeout
   * - must-revalidate
     - Force revalidation on expired cache

Performance Metrics
-------------------

The Cache Middleware provides built-in performance monitoring:

Timing Metrics
~~~~~~~~~~~~~~

.. code-block:: python

   # Example metrics collected
   {
       "cache_get_time": 0.001,      # Time to retrieve from cache
       "cache_set_time": 0.002,      # Time to store in cache  
       "backend_latency": 0.0015,    # Backend operation latency
       "total_request_time": 0.150   # Total request processing time
   }

Hit Rate Metrics
~~~~~~~~~~~~~~~~

.. code-block:: python

   # Cache performance metrics
   {
       "cache_hits": 850,
       "cache_misses": 150,
       "hit_rate": 0.85,             # 85% hit rate
       "total_requests": 1000
   }

Backend Health
~~~~~~~~~~~~~~

.. code-block:: python

   # Backend health status
   {
       "backend_type": "redis",
       "status": "healthy",
       "connection_pool_size": 10,
       "active_connections": 3,
       "last_health_check": "2024-01-15T10:30:00Z"
   }

Development Tools
-----------------

Testing Utilities
~~~~~~~~~~~~~~~~~

.. code-block:: python

   from cache_middleware.testing import (
       MockCacheBackend,
       TestCacheMiddleware,
       assert_cached,
       assert_not_cached
   )

   # Mock backend for testing
   mock_backend = MockCacheBackend()

   # Test assertions
   async def test_caching():
       await assert_cached("/api/data", timeout=300)
       await assert_not_cached("/api/dynamic")

Debug Mode
~~~~~~~~~~

Enable debug mode for development:

.. code-block:: python

   # Enable debug logging
   import logging
   logging.getLogger("cache_middleware").setLevel(logging.DEBUG)

   # Add debug headers
   app.add_middleware(
       CacheMiddleware, 
       backend=backend,
       debug=True  # Adds X-Cache-Key header
   )

Benchmarking
~~~~~~~~~~~~

Built-in benchmarking tools:

.. code-block:: python

   from cache_middleware.benchmark import benchmark_backend

   # Benchmark backend performance
   results = await benchmark_backend(
       backend=redis_backend,
       operations=1000,
       concurrency=10
   )

   print(f"Operations per second: {results['ops_per_second']}")

Migration Guide
---------------

From Version 1.x to 2.x
~~~~~~~~~~~~~~~~~~~~~~~~

Breaking changes and migration path:

.. code-block:: python

   # Version 1.x (factory pattern)
   from cache_middleware import CacheMiddleware, RedisBackendFactory
   
   factory = RedisBackendFactory(url="redis://localhost:6379")
   app.add_middleware(CacheMiddleware, backend_factory=factory)

   # Version 2.x (dependency injection)
   from cache_middleware.middleware import CacheMiddleware
   from cache_middleware.backends.redis_backend import RedisBackend
   
   backend = RedisBackend(url="redis://localhost:6379")
   app.add_middleware(CacheMiddleware, backend=backend)

Configuration Changes
~~~~~~~~~~~~~~~~~~~~~

Updated configuration format:

.. code-block:: python

   # Old configuration
   cache_config = {
       "backend_type": "redis",
       "redis_url": "redis://localhost:6379"
   }

   # New configuration
   backend = RedisBackend(url="redis://localhost:6379")
   app.add_middleware(CacheMiddleware, backend=backend)

Compatibility Notes
-------------------

Python Version Support
~~~~~~~~~~~~~~~~~~~~~~~

- **Python 3.8+**: Minimum supported version
- **Python 3.12**: Recommended version
- **Python 3.13**: Full support

Framework Compatibility
~~~~~~~~~~~~~~~~~~~~~~~

- **FastAPI**: Full support (recommended)
- **Starlette**: Full support
- **Django**: Limited support via ASGI
- **Flask**: Not supported (use Flask-Caching instead)

Redis Version Support
~~~~~~~~~~~~~~~~~~~~~

- **Redis 5.0+**: Minimum supported version
- **Redis 6.x**: Full support
- **Redis 7.x**: Full support with enhanced features

Dependencies
~~~~~~~~~~~~

Core dependencies and their versions:

.. code-block:: text

   fastapi>=0.68.0
   starlette>=0.14.0
   redis[hiredis]>=4.0.0
   loguru>=0.6.0
   pydantic>=1.8.0

Contributing
------------

API Design Guidelines
~~~~~~~~~~~~~~~~~~~~~

When contributing to the API:

1. **Type Hints**: All public functions must have complete type hints
2. **Docstrings**: Use NumPy-style docstrings for all public APIs
3. **Async/Await**: All I/O operations must be async
4. **Error Handling**: Fail gracefully, log errors appropriately
5. **Testing**: Maintain 100% test coverage for new APIs

Code Style
~~~~~~~~~~

- **Formatter**: Use `ruff format` for code formatting
- **Linter**: Use `ruff check` for code linting
- **Type Checker**: Use `mypy` for type checking
- **Documentation**: Use `sphinx` for API documentation

Pull Request Process
~~~~~~~~~~~~~~~~~~~~

1. Fork the repository
2. Create a feature branch
3. Add tests for new functionality
4. Update documentation
5. Run the full test suite
6. Submit pull request with clear description

See Also
--------

- :doc:`what-is` - Introduction to Cache Middleware
- :doc:`installation` - Installation instructions
- :doc:`user-guide` - Usage examples and tutorials
- :doc:`middleware-configuration` - Configuration options
- :doc:`extending-backends` - Custom backend development
