Cache Middleware Documentation
===============================

Welcome to Cache Middleware, a high-performance HTTP response caching solution for FastAPI and Starlette applications.

Cache Middleware provides transparent response caching with pluggable backends, following the Starlette middleware pattern for seamless integration.

.. toctree::
   :maxdepth: 2
   :caption: Contents:

   what-is
   installation
   user-guide
   middleware-configuration
   extending-backends
   api

Features
--------

* **Multiple Backends**: Redis, in-memory, and custom backend support
* **Decorator-based**: Simple ``@cache(timeout=300)`` decorator for endpoint caching
* **Cache-Control Support**: Respects HTTP Cache-Control headers
* **Flexible Configuration**: Environment-based or explicit configuration
* **Production Ready**: Comprehensive error handling and logging
* **Type Safe**: Full type hints and mypy support

Quick Start
-----------

Install cache-middleware:

.. code-block:: bash

   pip install cache-middleware

Add caching to your FastAPI application:

.. code-block:: python

   from fastapi import FastAPI
   from cache_middleware.middleware import CacheMiddleware
   from cache_middleware.backends.redis_backend import RedisBackend
   from cache_middleware.decorators import cache

   app = FastAPI()

   # Configure Redis backend
   redis_backend = RedisBackend(url="redis://localhost:6379")
   app.add_middleware(CacheMiddleware, backend=redis_backend)

   @app.get("/items")
   @cache(timeout=300)  # Cache for 5 minutes
   async def get_items():
       return {"items": [1, 2, 3, 4, 5]}

Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`
