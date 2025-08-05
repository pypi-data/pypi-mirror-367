"""
Cache Middleware - High-performance HTTP response caching for FastAPI and Starlette.

This package provides transparent response caching with pluggable backends.
"""

# Version info
__version__ = "0.1.6"

# Core middleware and decorator
from .middleware import CacheMiddleware
from .decorators import cache

# Helper functions for backend configuration
from .helpers import (
    create_redis_backend_from_env,
    create_memory_backend_from_env,
    auto_configure_backend,
    create_production_redis_backend,
    create_development_backend,
    get_backend_for_environment,
)

# Backend base class
from .backends import CacheBackend

# Commonly used backends (with optional import handling)
from .backends.memory_backend import MemoryBackend

# Optional backend imports with graceful handling
try:
    from .backends.redis_backend import RedisBackend
    _REDIS_AVAILABLE = True
except ImportError:
    RedisBackend = None
    _REDIS_AVAILABLE = False

try:
    from .backends.memcached_backend import MemcachedBackend
    _MEMCACHED_AVAILABLE = True
except ImportError:
    MemcachedBackend = None
    _MEMCACHED_AVAILABLE = False

# Public API
__all__ = [
    # Version
    "__version__",
    
    # Core components
    "CacheMiddleware",
    "cache",
    
    # Backend base class
    "CacheBackend",
    
    # Always available backends
    "MemoryBackend",
    
    # Optional backends (may be None if dependencies not installed)
    "RedisBackend",
    "MemcachedBackend",
    
    # Helper functions
    "create_redis_backend_from_env",
    "create_memory_backend_from_env", 
    "auto_configure_backend",
    "create_production_redis_backend",
    "create_development_backend",
    "get_backend_for_environment",
    
    # Availability flags
    "_REDIS_AVAILABLE",
    "_MEMCACHED_AVAILABLE",
]