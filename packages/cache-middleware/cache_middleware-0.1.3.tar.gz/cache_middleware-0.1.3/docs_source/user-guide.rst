User Guide
==========

This guide provides comprehensive examples of using Cache Middleware with FastAPI, covering different backends, configurations, and deployment scenarios.

Basic Usage
-----------

Simple FastAPI Application
~~~~~~~~~~~~~~~~~~~~~~~~~~~

Here's a minimal example to get started:

.. code-block:: python

   from fastapi import FastAPI
   from cache_middleware.middleware import CacheMiddleware
   from cache_middleware.backends.memory_backend import MemoryBackend
   from cache_middleware.decorators import cache

   app = FastAPI()

   # Configure in-memory backend
   memory_backend = MemoryBackend(max_size=1000)
   app.add_middleware(CacheMiddleware, backend=memory_backend)

   @app.get("/")
   @cache(timeout=300)  # Cache for 5 minutes
   async def read_root():
       return {"Hello": "World"}

   @app.get("/items/{item_id}")
   @cache(timeout=600)  # Cache for 10 minutes
   async def read_item(item_id: int, q: str = None):
       return {"item_id": item_id, "q": q}

Backend Configurations
----------------------

Redis Backend
~~~~~~~~~~~~~

Redis is recommended for production deployments:

**Basic Redis Setup:**

.. code-block:: python

   from cache_middleware.backends.redis_backend import RedisBackend

   # Basic configuration
   redis_backend = RedisBackend(url="redis://localhost:6379")
   app.add_middleware(CacheMiddleware, backend=redis_backend)

**Advanced Redis Configuration:**

.. code-block:: python

   # Production configuration with connection pooling
   redis_backend = RedisBackend(
       url="redis://prod-redis:6379",
       max_connections=20,
       retry_on_timeout=True,
       socket_keepalive=True,
       socket_keepalive_options={
           1: 1,  # TCP_KEEPIDLE
           2: 3,  # TCP_KEEPINTVL  
           3: 5,  # TCP_KEEPCNT
       },
       health_check_interval=30
   )
   app.add_middleware(CacheMiddleware, backend=redis_backend)

**Redis with Authentication:**

.. code-block:: python

   # Redis with password
   redis_backend = RedisBackend(
       url="redis://:password@redis-host:6379",
       max_connections=10
   )

   # Redis with SSL
   redis_backend = RedisBackend(
       url="rediss://redis-host:6380",
       password="secure-password",
       ssl_cert_reqs="required",
       ssl_ca_certs="/path/to/ca.pem"
   )

Memory Backend
~~~~~~~~~~~~~~

Perfect for development and testing:

.. code-block:: python

   from cache_middleware.backends.memory_backend import MemoryBackend

   # Basic memory backend
   memory_backend = MemoryBackend(max_size=1000)

   # Larger cache for development
   memory_backend = MemoryBackend(max_size=5000)
   app.add_middleware(CacheMiddleware, backend=memory_backend)

Environment-Based Configuration
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Use helper functions for environment-based setup:

.. code-block:: python

   from cache_middleware.helpers import auto_configure_backend
   import os

   # Automatically configure based on environment variables
   backend = auto_configure_backend()
   app.add_middleware(CacheMiddleware, backend=backend)

Set environment variables:

.. code-block:: bash

   # Use Redis backend
   export CACHE_BACKEND=redis
   export REDIS_URL=redis://localhost:6379
   export REDIS_MAX_CONNECTIONS=20

   # Use memory backend
   export CACHE_BACKEND=memory
   export MEMORY_CACHE_SIZE=1000

Advanced Usage Examples
-----------------------

POST Requests with Body Caching
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Cache POST requests based on their body content:

.. code-block:: python

   from fastapi import Body

   @app.post("/calculate")
   @cache(timeout=300)
   async def calculate(data: dict = Body(...)):
       # Expensive calculation
       numbers = data.get("numbers", [])
       result = sum(x ** 2 for x in numbers)
       return {"input": data, "result": result}

Different Cache Timeouts
~~~~~~~~~~~~~~~~~~~~~~~~

Use different timeouts for different types of data:

.. code-block:: python

   @app.get("/users/{user_id}")
   @cache(timeout=1800)  # 30 minutes for user data
   async def get_user(user_id: int):
       return {"user_id": user_id, "name": f"User {user_id}"}

   @app.get("/stats")
   @cache(timeout=60)  # 1 minute for frequently changing stats
   async def get_stats():
       return {"requests": 12345, "active_users": 678}

   @app.get("/config")
   @cache(timeout=3600)  # 1 hour for rarely changing config
   async def get_config():
       return {"version": "1.0", "features": ["caching", "auth"]}

Cache-Control Header Support
~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Respect HTTP Cache-Control headers:

.. code-block:: python

   @app.get("/data")
   @cache(timeout=300)
   async def get_data():
       return {"data": "cached_value"}

   # Client usage:
   # GET /data - Returns cached response
   # GET /data with "Cache-Control: no-cache" - Forces fresh response
   # GET /data with "Cache-Control: no-store" - Bypasses cache entirely

Docker Deployment
-----------------

Complete Docker Setup
~~~~~~~~~~~~~~~~~~~~~~

**Dockerfile:**

.. code-block:: dockerfile

   FROM python:3.12-slim

   WORKDIR /app

   # Install dependencies
   COPY requirements.txt .
   RUN pip install -r requirements.txt

   # Copy application
   COPY . .

   # Expose port
   EXPOSE 8000

   # Run application
   CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]

**docker-compose.yml:**

.. code-block:: yaml

   version: '3.8'
   services:
     web:
       build: .
       ports:
         - "8000:8000"
       environment:
         - CACHE_BACKEND=redis
         - REDIS_URL=redis://redis:6379
         - REDIS_MAX_CONNECTIONS=20
       depends_on:
         - redis
       healthcheck:
         test: ["CMD", "curl", "-f", "http://localhost:8000/health"]
         interval: 30s
         timeout: 10s
         retries: 3

     redis:
       image: redis:7-alpine
       ports:
         - "6379:6379"
       volumes:
         - redis-data:/data
       command: redis-server --appendonly yes
       healthcheck:
         test: ["CMD", "redis-cli", "ping"]
         interval: 10s
         timeout: 5s
         retries: 3

   volumes:
     redis-data:

Redis Development Setup
~~~~~~~~~~~~~~~~~~~~~~~

For local development with Redis:

.. code-block:: yaml

   # docker-compose-dev.yml
   services:
     redis:
       image: redis:7-alpine
       ports:
         - "6379:6379"
       volumes:
         - ./redis-data:/data

Run with:

.. code-block:: bash

   docker-compose -f docker-compose-dev.yml up -d

Memcached Alternative
~~~~~~~~~~~~~~~~~~~~~

For Memcached backend (custom implementation):

.. code-block:: yaml

   services:
     memcached:
       image: memcached:1.6-alpine
       ports:
         - "11211:11211"
       command: memcached -m 64

Production Configuration
------------------------

Multi-Environment Setup
~~~~~~~~~~~~~~~~~~~~~~~~

**Development (main.py):**

.. code-block:: python

   import os
   from cache_middleware.helpers import get_backend_for_environment

   app = FastAPI()

   # Auto-configure based on environment
   env = os.getenv("ENVIRONMENT", "development")
   backend = get_backend_for_environment(env)
   app.add_middleware(CacheMiddleware, backend=backend)

**Environment Variables:**

.. code-block:: bash

   # Development
   ENVIRONMENT=development

   # Production
   ENVIRONMENT=production
   REDIS_URL=redis://prod-redis-cluster:6379
   REDIS_MAX_CONNECTIONS=50

High Availability Redis
~~~~~~~~~~~~~~~~~~~~~~~

For production with Redis Cluster or Sentinel:

.. code-block:: python

   # Redis Cluster
   redis_backend = RedisBackend(
       url="redis://redis-cluster-node1:6379",
       max_connections=50,
       retry_on_timeout=True,
       health_check_interval=30,
       socket_keepalive=True
   )

   # Redis Sentinel (requires custom configuration)
   # See Redis documentation for Sentinel setup

Monitoring and Observability
~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Enable comprehensive logging:

.. code-block:: python

   from cache_middleware.logger_config import configure_logger, logger
   import sys

   # Configure detailed logging
   configure_logger()
   logger.add(
       "cache_middleware.log", 
       rotation="10 MB", 
       level="INFO",
       format="{time} | {level} | {message}"
   )
   logger.add(sys.stderr, level="DEBUG")

Performance Testing
-------------------

Load Testing Setup
~~~~~~~~~~~~~~~~~~

Test caching performance with wrk or Apache Benchmark:

.. code-block:: bash

   # Install wrk (Ubuntu/Debian)
   sudo apt install wrk

   # Test without cache
   wrk -t4 -c100 -d30s http://localhost:8000/expensive-operation

   # Test with cache (second run should be much faster)
   wrk -t4 -c100 -d30s http://localhost:8000/expensive-operation

Benchmark different backends:

.. code-block:: python

   import time
   import asyncio
   from cache_middleware.backends.memory_backend import MemoryBackend
   from cache_middleware.backends.redis_backend import RedisBackend

   async def benchmark_backend(backend, iterations=1000):
       start_time = time.time()
       
       for i in range(iterations):
           await backend.set(f"key_{i}", f"value_{i}", 300)
           value = await backend.get(f"key_{i}")
       
       end_time = time.time()
       print(f"Backend {type(backend).__name__}: {end_time - start_time:.2f}s")

Cache Warming
~~~~~~~~~~~~~

Pre-populate cache for better performance:

.. code-block:: python

   @app.on_event("startup")
   async def warm_cache():
       """Warm up cache with frequently accessed data"""
       # Pre-cache common queries
       backend = app.state.cache_backend
       await backend.set("config:version", "1.0", 3600)
       await backend.set("stats:global", '{"users": 1000}', 300)

Troubleshooting
---------------

Common Issues
~~~~~~~~~~~~~

**Cache Not Working:**

1. Verify the endpoint has the ``@cache`` decorator
2. Check middleware is properly registered
3. Ensure backend is correctly configured

**Redis Connection Issues:**

.. code-block:: python

   # Test Redis connectivity
   import redis
   r = redis.Redis.from_url("redis://localhost:6379")
   try:
       r.ping()
       print("Redis connection successful")
   except redis.ConnectionError:
       print("Redis connection failed")

**Performance Issues:**

1. Monitor cache hit rates through logging
2. Adjust cache timeouts based on data freshness requirements
3. Consider cache key design for optimal distribution

Debug Mode
~~~~~~~~~~

Enable debug logging to troubleshoot caching behavior:

.. code-block:: python

   import logging
   from cache_middleware.logger_config import logger

   # Enable debug logging
   logger.add(sys.stderr, level="DEBUG")

   # This will show cache hits, misses, and key generation
   @app.get("/debug")
   @cache(timeout=60)
   async def debug_endpoint():
       return {"timestamp": time.time()}

Next Steps
----------

- Learn about :doc:`middleware-configuration` for advanced settings
- Explore :doc:`extending-backends` to create custom backends
- Check the :doc:`api` reference for detailed documentation
