# Cache Middleware

A high-performance HTTP response caching solution for FastAPI and Starlette applications.

Cache Middleware provides transparent response caching with pluggable backends, following the Starlette middleware pattern for seamless integration.

[![PyPI Version](https://img.shields.io/pypi/v/cache-middleware.svg)](https://pypi.org/project/cache-middleware/)
[![Python Version](https://img.shields.io/pypi/pyversions/cache-middleware.svg)](https://pypi.org/project/cache-middleware/)
[![License](https://img.shields.io/pypi/l/cache-middleware.svg)](https://github.com/impalah/cache-middleware/blob/main/LICENSE)

## ✨ Features

- **🔄 Multiple Backends**: Redis, Memcached, in-memory, and custom backend support
- **🎯 Decorator-based**: Simple `@cache(timeout=300)` decorator for endpoint caching
- **📋 Cache-Control Support**: Respects HTTP Cache-Control headers
- **⚙️ Flexible Configuration**: Environment-based or explicit configuration
- **🚀 Production Ready**: Comprehensive error handling and logging
- **🔒 Type Safe**: Full type hints and mypy support
- **📦 Modular Installation**: Install only the backends you need

## 📖 Documentation

Complete documentation is available at: **https://impalah.github.io/cache-middleware/**

## 🚀 Quick Start

### Installation

**Basic installation (memory backend only):**

```bash
pip install cache-middleware
```

**With Redis backend:**

```bash
pip install cache-middleware[redis]
```

**With Memcached backend:**

```bash
pip install cache-middleware[memcached]
```

**With all backends:**

```bash
pip install cache-middleware[all]
```

### Basic Usage

```python
from fastapi import FastAPI
from cache_middleware.middleware import CacheMiddleware
from cache_middleware.backends.memory_backend import MemoryBackend
from cache_middleware.decorators import cache

app = FastAPI()

# Configure memory backend
memory_backend = MemoryBackend(max_size=1000)
app.add_middleware(CacheMiddleware, backend=memory_backend)

@app.get("/items")
@cache(timeout=300)  # Cache for 5 minutes
async def get_items():
    return {"items": [1, 2, 3, 4, 5]}
```

### Redis Backend Example

```python
from cache_middleware.backends.redis_backend import RedisBackend

# Configure Redis backend
redis_backend = RedisBackend(url="redis://localhost:6379")
app.add_middleware(CacheMiddleware, backend=redis_backend)
```

## 🔧 Backend Options

### Memory Backend

- ✅ No external dependencies
- ✅ Perfect for development and testing
- ✅ LRU eviction policy
- ✅ Configurable size limits

### Redis Backend

- ✅ Production-ready distributed caching
- ✅ Persistence and high availability
- ✅ Clustering support
- ✅ High performance with hiredis

### Memcached Backend

- ✅ Lightweight distributed caching
- ✅ Simple and fast
- ✅ Wide ecosystem support

### Custom Backends

- ✅ Implement your own backend
- ✅ Simple abstract interface
- ✅ Easy integration

## 📋 Requirements

- **Python**: 3.12 or higher
- **FastAPI**: 0.116.1 or higher
- **Redis**: Optional, required only for Redis backend
- **Memcached**: Optional, required only for Memcached backend

## 🔗 Links

- **📖 Documentation**: https://impalah.github.io/cache-middleware/
- **📦 PyPI**: https://pypi.org/project/cache-middleware/
- **🐙 GitHub**: https://github.com/impalah/cache-middleware
- **🐛 Issues**: https://github.com/impalah/cache-middleware/issues

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🤝 Contributing

Contributions are welcome! Please read our [Contributing Guide](https://impalah.github.io/cache-middleware/) for details on our code of conduct and the process for submitting pull requests.

## 🚀 Getting Started

Ready to add caching to your FastAPI application? Check out our [User Guide](https://impalah.github.io/cache-middleware/user-guide.html) for detailed examples and best practices.

For advanced configuration and custom backends, see our [Configuration Guide](https://impalah.github.io/cache-middleware/middleware-configuration.html).

---

**Cache Middleware** - Making FastAPI applications faster, one cache at a time! 🚀
