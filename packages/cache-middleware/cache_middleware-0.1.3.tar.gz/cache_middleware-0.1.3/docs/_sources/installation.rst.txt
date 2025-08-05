Installation
============

Cache Middleware can be installed using various Python package managers. Choose the method that best fits your development workflow.

Requirements
------------

- **Python**: 3.12 or higher
- **FastAPI**: 0.116.1 or higher
- **Redis**: Optional, required only for Redis backend
- **Memcached**: Optional, required only for Memcached backend

Basic Installation
------------------

The base package includes only core functionality with the in-memory backend. Additional backends can be installed as needed.

Core Package Only
~~~~~~~~~~~~~~~~~~

Install just the core cache middleware (includes Memory backend only):

.. code-block:: bash

   pip install cache-middleware

This provides:
- Memory backend for development and testing
- Core middleware functionality
- All decorators and utilities

Backend-Specific Installation
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Install with specific backend support:

**Redis Backend:**

.. code-block:: bash

   pip install cache-middleware[redis]

**Memcached Backend:**

.. code-block:: bash

   pip install cache-middleware[memcached]

**Multiple Backends:**

.. code-block:: bash

   pip install cache-middleware[redis,memcached]

**All Available Backends:**

.. code-block:: bash

   pip install cache-middleware[all]

Package Manager Examples
~~~~~~~~~~~~~~~~~~~~~~~~

**pip:**

.. code-block:: bash

   # Core only
   pip install cache-middleware
   
   # With Redis backend
   pip install cache-middleware[redis]
   
   # With all backends
   pip install cache-middleware[all]

For development with additional tools:

.. code-block:: bash

   pip install cache-middleware[all,dev]

**uv (Recommended):**

.. code-block:: bash

   # Core only
   uv add cache-middleware
   
   # With Redis backend
   uv add "cache-middleware[redis]"
   
   # With all backends
   uv add "cache-middleware[all]"

For development dependencies:

.. code-block:: bash

   uv add "cache-middleware[all]" --group dev

**Poetry:**

.. code-block:: bash

   # Core only
   poetry add cache-middleware
   
   # With Redis backend
   poetry add "cache-middleware[redis]"
   
   # With all backends
   poetry add "cache-middleware[all]"

For development dependencies:

.. code-block:: bash

   poetry add "cache-middleware[all]" --group dev

**pipenv:**

.. code-block:: bash

   # Core only
   pipenv install cache-middleware
   
   # With Redis backend
   pipenv install "cache-middleware[redis]"

For development dependencies:

.. code-block:: bash

   pipenv install "cache-middleware[all]" --dev

conda
~~~~~

For Anaconda/Miniconda environments:

.. code-block:: bash

   # Note: Conda packages may not support optional dependencies
   # Install base package and then add backend dependencies manually
   conda install -c conda-forge cache-middleware
   pip install redis[hiredis]  # For Redis backend
   pip install aiomcache       # For Memcached backend

Backend Dependencies
--------------------

The package now supports modular installation of backend dependencies:

Redis Backend
~~~~~~~~~~~~~

The Redis backend requires additional dependencies installed via extras:

.. code-block:: bash

   pip install cache-middleware[redis]

This includes:
- ``redis[hiredis]>=6.2.0`` - Redis client with hiredis for performance
- Hiredis provides faster Redis protocol parsing

**Manual Installation:**

.. code-block:: bash

   pip install cache-middleware
   pip install redis[hiredis]

Memcached Backend  
~~~~~~~~~~~~~~~~~

The Memcached backend requires additional dependencies:

.. code-block:: bash

   pip install cache-middleware[memcached]

This includes:
- ``aiomcache>=0.8.2`` - Async Memcached client

**Manual Installation:**

.. code-block:: bash

   pip install cache-middleware
   pip install aiomcache

Memory Backend
~~~~~~~~~~~~~~

The in-memory backend has no external dependencies and is included in the core package.

All Backends
~~~~~~~~~~~~

To install all available backends at once:

.. code-block:: bash

   pip install cache-middleware[all]

This is equivalent to:

.. code-block:: bash

   pip install cache-middleware[redis,memcached]

Development Installation
------------------------

For contributing to Cache Middleware or running from source:

From Source
~~~~~~~~~~~

.. code-block:: bash

   git clone https://github.com/impalah/cache-middleware.git
   cd cache-middleware
   uv sync

This will install all dependencies including development tools and all backends.

Development Dependencies
~~~~~~~~~~~~~~~~~~~~~~~~

Development installation includes all backends plus development tools:

- ``pytest>=8.3.5`` - Testing framework
- ``pytest-asyncio>=0.26.0`` - Async test support
- ``pytest-cov>=6.0.0`` - Coverage reporting
- ``mypy>=1.15.0`` - Type checking
- ``ruff>=0.11.0`` - Linting and formatting
- ``bandit>=1.8.3`` - Security scanning

Docker Installation
-------------------

For containerized environments, choose the appropriate backend extras:

**Memory Backend Only (minimal):**

.. code-block:: dockerfile

   FROM python:3.12-slim

   # Install core cache-middleware only
   RUN pip install cache-middleware

   # Copy your application
   COPY . /app
   WORKDIR /app

   # Run your FastAPI app
   CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]

**With Redis Backend:**

.. code-block:: dockerfile

   FROM python:3.12-slim

   # Install cache-middleware with Redis support
   RUN pip install cache-middleware[redis]

   # Copy your application
   COPY . /app
   WORKDIR /app

   # Run your FastAPI app
   CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]

**With All Backends:**

.. code-block:: dockerfile

   FROM python:3.12-slim

   # Install cache-middleware with all backends
   RUN pip install cache-middleware[all]

   # Copy your application
   COPY . /app
   WORKDIR /app

   # Run your FastAPI app
   CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]

Docker Compose Example
~~~~~~~~~~~~~~~~~~~~~~

Complete setup with Redis backend:

.. code-block:: yaml

   version: '3.8'
   services:
     web:
       build: .
       ports:
         - "8000:8000"
       environment:
         - REDIS_URL=redis://redis:6379
       depends_on:
         - redis
     
     redis:
       image: redis:7-alpine
       ports:
         - "6379:6379"

For multi-backend development environment:

.. code-block:: yaml

   version: '3.8'
   services:
     web:
       build: .
       ports:
         - "8000:8000"
       environment:
         - REDIS_URL=redis://redis:6379
         - MEMCACHED_URL=memcached:11211
       depends_on:
         - redis
         - memcached
     
     redis:
       image: redis:7-alpine
       ports:
         - "6379:6379"
       volumes:
         - redis-data:/data
         
     memcached:
       image: memcached:latest
       ports:
         - "11211:11211"
         
   volumes:
     redis-data:

Environment Setup
-----------------

Depending on your chosen backend, you may need to set up external services:

Memory Backend Setup
~~~~~~~~~~~~~~~~~~~~

No external setup required. The memory backend works out of the box.

Redis Setup
~~~~~~~~~~~

If using the Redis backend, you'll need a Redis server. Here are common setup methods:

**Local Redis with Docker:**

.. code-block:: bash

   docker run -d --name redis -p 6379:6379 redis:7-alpine

**Docker Compose (for development):**

.. code-block:: yaml

   services:
     redis:
       image: redis:7-alpine
       ports:
         - "6379:6379"
       volumes:
         - redis-data:/data
   
   volumes:
     redis-data:

**System Installation:**

Ubuntu/Debian:

.. code-block:: bash

   sudo apt update
   sudo apt install redis-server

macOS with Homebrew:

.. code-block:: bash

   brew install redis
   brew services start redis

Windows with WSL:

.. code-block:: bash

   sudo apt install redis-server
   sudo service redis-server start

Memcached Setup
~~~~~~~~~~~~~~~

If using the Memcached backend, you'll need a Memcached server:

**Local Memcached with Docker:**

.. code-block:: bash

   docker run -d --name memcached -p 11211:11211 memcached:latest

**System Installation:**

Ubuntu/Debian:

.. code-block:: bash

   sudo apt update
   sudo apt install memcached

macOS with Homebrew:

.. code-block:: bash

   brew install memcached
   brew services start memcached

Windows:
Download from the official Memcached website or use Docker.

Verification
------------

Verify your installation by running:

.. code-block:: python

   import cache_middleware
   print(cache_middleware.__version__)

Backend-Specific Verification
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

**Memory Backend (always available):**

.. code-block:: python

   from cache_middleware.backends.memory_backend import MemoryBackend
   backend = MemoryBackend(max_size=100)
   print("Memory backend available")

**Redis Backend:**

.. code-block:: python

   try:
       from cache_middleware.backends.redis_backend import RedisBackend
       print("Redis backend available")
   except ImportError as e:
       print(f"Redis backend not available: {e}")

**Memcached Backend:**

.. code-block:: python

   try:
       from cache_middleware.backends.memcached_backend import MemcachedBackend
       print("Memcached backend available")
   except ImportError as e:
       print(f"Memcached backend not available: {e}")

Complete Example
~~~~~~~~~~~~~~~~

Test with a simple FastAPI app:

.. code-block:: python

   from fastapi import FastAPI
   from cache_middleware.middleware import CacheMiddleware
   from cache_middleware.backends.memory_backend import MemoryBackend
   from cache_middleware.decorators import cache

   app = FastAPI()

   # Use memory backend for testing (always available)
   memory_backend = MemoryBackend(max_size=100)
   app.add_middleware(CacheMiddleware, backend=memory_backend)

   @app.get("/test")
   @cache(timeout=60)
   async def test_endpoint():
       return {"message": "Cache middleware is working!"}

   if __name__ == "__main__":
       import uvicorn
       uvicorn.run(app, host="0.0.0.0", port=8000)

Run this and visit ``http://localhost:8000/test`` to verify caching is working.

Troubleshooting
---------------

Common Issues
~~~~~~~~~~~~~

**Import Error:**

.. code-block:: text

   ImportError: No module named 'cache_middleware'

Solution: Ensure you're in the correct virtual environment and cache-middleware is installed.

**Backend Import Error:**

.. code-block:: text

   ImportError: Redis backend requires 'redis[hiredis]'. Install with: pip install cache-middleware[redis]

Solution: Install the appropriate backend extras:

.. code-block:: bash

   # For Redis backend
   pip install cache-middleware[redis]
   
   # For Memcached backend  
   pip install cache-middleware[memcached]
   
   # For all backends
   pip install cache-middleware[all]

**Redis Connection Error:**

.. code-block:: text

   redis.exceptions.ConnectionError: Error connecting to Redis

Solution: Verify Redis is running and accessible at the configured URL.

**Memcached Connection Error:**

.. code-block:: text

   OSError: [Errno 111] Connection refused

Solution: Verify Memcached is running and accessible at the configured host/port.

**Version Conflicts:**

If you encounter dependency conflicts, try creating a fresh virtual environment:

.. code-block:: bash

   python -m venv fresh-env
   source fresh-env/bin/activate  # On Windows: fresh-env\\Scripts\\activate
   pip install cache-middleware[all]

**Performance Issues:**

For optimal performance with Redis, ensure you have hiredis installed (included with redis extras):

.. code-block:: bash

   pip install cache-middleware[redis]  # Includes hiredis

Getting Help
~~~~~~~~~~~~

If you encounter issues:

1. Check the `GitHub Issues <https://github.com/impalah/cache-middleware/issues>`_
2. Review the configuration documentation
3. Enable debug logging to diagnose issues
4. Create a minimal reproduction case

Next Steps
----------

After installation, proceed to the :doc:`user-guide` to learn how to configure and use Cache Middleware in your FastAPI applications.
