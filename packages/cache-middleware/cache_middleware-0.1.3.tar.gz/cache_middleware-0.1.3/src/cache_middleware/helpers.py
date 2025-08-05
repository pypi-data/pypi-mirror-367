"""
Helper functions for common backend configurations.

This module provides convenience functions to create and configure
cache backends using environment variables and common patterns.
It simplifies backend setup for different deployment environments.
"""
import os
from typing import Optional, TYPE_CHECKING

if TYPE_CHECKING:
    from cache_middleware.backends.redis_backend import RedisBackend
    from cache_middleware.backends.memcached_backend import MemcachedBackend

# Optional imports with proper error handling
try:
    from cache_middleware.backends.redis_backend import RedisBackend
    _REDIS_AVAILABLE = True
except ImportError:
    _REDIS_AVAILABLE = False

try:
    from cache_middleware.backends.memcached_backend import MemcachedBackend
    _MEMCACHED_AVAILABLE = True
except ImportError:
    _MEMCACHED_AVAILABLE = False

from cache_middleware.backends.memory_backend import MemoryBackend
from cache_middleware.backends import CacheBackend


def create_redis_backend_from_env() -> "RedisBackend":
    """
    Create Redis backend using environment variables.
    
    This function reads Redis configuration from environment variables,
    making it easy to configure the backend for different deployment
    environments without code changes.
    
    Returns
    -------
    RedisBackend
        Configured Redis backend instance
        
    Raises
    ------
    ImportError
        If redis backend dependencies are not installed
        
    Environment Variables
    --------------------
    REDIS_URL : str, default="redis://localhost:6379"
        Redis connection URL
    REDIS_MAX_CONNECTIONS : int, default=10
        Maximum number of connections in the pool
    REDIS_PASSWORD : str, optional
        Redis authentication password
    REDIS_RETRY_ON_TIMEOUT : bool, default=True
        Whether to retry operations on timeout
        
    Examples
    --------
    >>> # Set environment variables
    >>> os.environ["REDIS_URL"] = "redis://prod-redis:6379"
    >>> os.environ["REDIS_MAX_CONNECTIONS"] = "20"
    >>> backend = create_redis_backend_from_env()
    """
    if not _REDIS_AVAILABLE:
        raise ImportError(
            "Redis backend requires 'redis[hiredis]'. "
            "Install with: pip install cache-middleware[redis]"
        )
    
    return RedisBackend(
        url=os.getenv("REDIS_URL", "redis://localhost:6379"),
        max_connections=int(os.getenv("REDIS_MAX_CONNECTIONS", "10")),
        password=os.getenv("REDIS_PASSWORD"),
        retry_on_timeout=os.getenv("REDIS_RETRY_ON_TIMEOUT", "true").lower() == "true"
    )


def create_memory_backend_from_env() -> MemoryBackend:
    """
    Create in-memory backend using environment variables.
    
    Returns
    -------
    MemoryBackend
        Configured in-memory backend instance
        
    Environment Variables
    --------------------
    MEMORY_CACHE_SIZE : int, default=1000
        Maximum number of cache entries to store
        
    Examples
    --------
    >>> os.environ["MEMORY_CACHE_SIZE"] = "500"
    >>> backend = create_memory_backend_from_env()
    """
    return MemoryBackend(
        max_size=int(os.getenv("MEMORY_CACHE_SIZE", "1000"))
    )


def auto_configure_backend() -> CacheBackend:
    """
    Auto-configure backend based on environment variables.
    
    This function automatically selects and configures the appropriate
    backend based on the CACHE_BACKEND environment variable.
    
    Returns
    -------
    CacheBackend
        Configured backend instance
        
    Environment Variables
    --------------------
    CACHE_BACKEND : str, default="memory"
        Backend type to use ("redis" or "memory")
        
    Raises
    ------
    ValueError
        If an unknown backend type is specified
        
    Examples
    --------
    >>> os.environ["CACHE_BACKEND"] = "redis"
    >>> backend = auto_configure_backend()  # Returns RedisBackend
    """
    backend_type = os.getenv("CACHE_BACKEND", "memory").lower()
    
    if backend_type == "redis":
        return create_redis_backend_from_env()
    elif backend_type == "memory":
        return create_memory_backend_from_env()
    else:
        raise ValueError(f"Unknown backend type from env: {backend_type}")


def create_production_redis_backend() -> "RedisBackend":
    """
    Create Redis backend optimized for production.
    
    This function creates a Redis backend with production-ready settings
    including connection pooling, keepalive, and health checks.
    
    Returns
    -------
    RedisBackend
        Production-optimized Redis backend
        
    Raises
    ------
    ImportError
        If redis backend dependencies are not installed
        
    Environment Variables
    --------------------
    REDIS_URL : str, default="redis://localhost:6379"
        Redis connection URL
    """
    if not _REDIS_AVAILABLE:
        raise ImportError(
            "Redis backend requires 'redis[hiredis]'. "
            "Install with: pip install cache-middleware[redis]"
        )
    
    return RedisBackend(
        url=os.getenv("REDIS_URL", "redis://localhost:6379"),
        max_connections=100,
        retry_on_timeout=True,
        socket_keepalive=True,
        socket_keepalive_options={
            1: 1,  # TCP_KEEPIDLE
            2: 3,  # TCP_KEEPINTVL  
            3: 5,  # TCP_KEEPCNT
        },
        health_check_interval=30
    )


def create_development_backend() -> MemoryBackend:
    """
    Create in-memory backend optimized for development.
    
    This function creates a small in-memory cache suitable for
    development and testing environments.
    
    Returns
    -------
    MemoryBackend
        Development-optimized memory backend
    """
    return MemoryBackend(max_size=500)


def get_backend_for_environment(env: str = None) -> CacheBackend:
    """
    Get backend configured for a specific environment.
    
    This function provides environment-specific backend configurations
    with sensible defaults for common deployment scenarios.
    
    Parameters
    ----------
    env : str, optional
        Environment name ("development", "production", "testing").
        If None, uses the ENVIRONMENT environment variable.
        
    Returns
    -------
    CacheBackend
        Backend configured for the specified environment
        
    Environment Variables
    --------------------
    ENVIRONMENT : str, default="development"
        Deployment environment when env parameter is None
        
    Examples
    --------
    >>> # Explicit environment
    >>> backend = get_backend_for_environment("production")
    >>> 
    >>> # From environment variable
    >>> os.environ["ENVIRONMENT"] = "production"
    >>> backend = get_backend_for_environment()
    """
    if env is None:
        env = os.getenv("ENVIRONMENT", "development").lower()
    
    if env == "production":
        return create_production_redis_backend()
    elif env == "development":
        return create_development_backend()
    elif env == "testing":
        return MemoryBackend(max_size=100)  # Small cache for tests
    else:
        return auto_configure_backend()
