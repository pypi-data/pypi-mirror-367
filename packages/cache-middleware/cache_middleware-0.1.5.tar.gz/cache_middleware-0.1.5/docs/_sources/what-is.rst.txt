What is Cache Middleware?
=========================

Cache Middleware is a high-performance HTTP response caching solution designed specifically for FastAPI and Starlette applications. It provides transparent, configurable caching that can significantly improve your application's performance and reduce server load.

Overview
--------

Cache Middleware follows the **Starlette middleware pattern**, integrating seamlessly into your application's request/response cycle. It intercepts HTTP requests, checks for cached responses, and serves them when available, while automatically caching new responses according to your configuration.

Key Concepts
------------

Middleware Pattern
~~~~~~~~~~~~~~~~~~

Cache Middleware implements the Starlette ``BaseHTTPMiddleware`` interface, which means:

- **Transparent Integration**: Works with any FastAPI or Starlette application without code changes
- **Request Lifecycle**: Intercepts requests before they reach your endpoints
- **Response Processing**: Captures and caches responses automatically
- **Standard Interface**: Follows established patterns familiar to Starlette/FastAPI developers

Decorator-Driven Caching
~~~~~~~~~~~~~~~~~~~~~~~~~

The caching behavior is controlled through a simple decorator pattern:

.. code-block:: python

   from cache_middleware.decorators import cache

   @app.get("/expensive-operation")
   @cache(timeout=300)  # Cache for 5 minutes
   async def expensive_operation():
       # Expensive computation here
       return {"result": "computed_value"}

The ``@cache`` decorator:

- Marks endpoints for caching without modifying their logic
- Sets cache expiration times per endpoint
- Allows fine-grained control over what gets cached

Backend Architecture
~~~~~~~~~~~~~~~~~~~~

Cache Middleware uses a pluggable backend system:

- **Redis Backend**: For distributed, persistent caching in production
- **Memory Backend**: For development, testing, and single-instance deployments
- **Custom Backends**: Implement your own storage solutions (Memcached, database, etc.)

All backends implement the same interface, making it easy to switch between them:

.. code-block:: python

   # Development setup
   memory_backend = MemoryBackend(max_size=1000)
   app.add_middleware(CacheMiddleware, backend=memory_backend)

   # Production setup  
   redis_backend = RedisBackend(url="redis://prod-redis:6379")
   app.add_middleware(CacheMiddleware, backend=redis_backend)

How It Works
------------

Cache Middleware operates through the following process:

1. **Request Interception**: Middleware intercepts incoming HTTP requests
2. **Endpoint Discovery**: Finds the target endpoint function in the application routes
3. **Cache Check**: Verifies if the endpoint has the ``@cache`` decorator
4. **Cache Key Generation**: Creates unique keys based on method, path, query parameters, and request body
5. **Cache Lookup**: Attempts to retrieve cached response for the key
6. **Response Handling**: Either serves cached response or calls the endpoint and caches the result

Cache Key Strategy
~~~~~~~~~~~~~~~~~~

Cache keys are generated using:

- HTTP method (GET, POST, etc.)
- Request path
- Query parameters (sorted for consistency)
- Request body content
- SHA256 hash for efficient storage

This ensures that different requests are cached separately while identical requests share the same cache entry.

HTTP Cache-Control Support
~~~~~~~~~~~~~~~~~~~~~~~~~~~

Cache Middleware respects standard HTTP caching headers:

- ``Cache-Control: no-store`` - Bypasses caching entirely
- ``Cache-Control: no-cache`` - Forces fresh response (updates cache)

This allows clients to control caching behavior when needed.

Use Cases
---------

Cache Middleware is ideal for:

**API Responses**
  Cache expensive database queries, API calls, or computation results

**Content Delivery**
  Serve frequently requested content without hitting your backend

**Rate Limiting Support**
  Reduce load on rate-limited external APIs

**Microservices**
  Cache responses between service calls in distributed architectures

**Development Speed**
  Speed up development by caching slow external dependencies

Benefits
--------

Performance
~~~~~~~~~~~

- **Reduced Latency**: Serve responses from cache in microseconds
- **Lower CPU Usage**: Avoid re-executing expensive operations
- **Reduced I/O**: Minimize database and external API calls

Scalability
~~~~~~~~~~~

- **Higher Throughput**: Handle more requests with the same resources
- **Backend Protection**: Reduce load on databases and external services
- **Horizontal Scaling**: Redis backend supports distributed caching

Flexibility
~~~~~~~~~~~

- **Granular Control**: Cache only specific endpoints with custom timeouts
- **Multiple Backends**: Choose the right storage for your needs
- **Environment Adaptation**: Different configurations for dev/staging/production

Developer Experience
~~~~~~~~~~~~~~~~~~~~

- **Simple Integration**: Add caching with just a decorator and middleware registration
- **Type Safety**: Full type hints for better IDE support
- **Observability**: Comprehensive logging for cache hits/misses and errors
