"""
Redis cache backend implementation.

This module provides a Redis-based cache backend for production use.
It supports connection pooling, automatic reconnection, and comprehensive
error handling.
"""
try:
    import redis.asyncio as aioredis
except ImportError:
    raise ImportError(
        "Redis backend requires 'redis[hiredis]'. "
        "Install with: pip install cache-middleware[redis]"
    )

from typing import Optional
from cache_middleware.backends import CacheBackend
from cache_middleware.logger_config import logger


class RedisBackend(CacheBackend):
    """
    Redis cache backend for production deployments.
    
    This backend uses Redis as the caching layer, providing persistence,
    clustering support, and high performance. It implements lazy connection
    initialization and comprehensive error handling.
    
    Parameters
    ----------
    url : str, default="redis://localhost:6379"
        Redis connection URL (e.g., "redis://localhost:6379", "rediss://secure:6380")
    **kwargs
        Additional keyword arguments passed to redis.asyncio.from_url()
        Common options include:
        - max_connections: Maximum connections in the pool
        - retry_on_timeout: Whether to retry on timeout
        - password: Redis password
        - socket_keepalive: Enable TCP keepalive
        
    Attributes
    ----------
    url : str
        Redis connection URL
    connection_kwargs : dict
        Additional connection parameters
    redis : Optional[aioredis.Redis]
        Redis client instance (initialized lazily)
        
    Examples
    --------
    >>> # Basic usage
    >>> backend = RedisBackend(url="redis://localhost:6379")
    >>> 
    >>> # With custom configuration
    >>> backend = RedisBackend(
    ...     url="redis://localhost:6379",
    ...     max_connections=20,
    ...     retry_on_timeout=True,
    ...     password="secret"
    ... )
    """
    
    def __init__(self, url: str = "redis://localhost:6379", **kwargs):
        """
        Initialize the Redis cache backend.
        
        Parameters
        ----------
        url : str, default="redis://localhost:6379"
            Redis connection URL
        **kwargs
            Additional connection parameters for Redis client
        """
        self.url = url
        self.connection_kwargs = kwargs
        self.redis = None
    
    async def _ensure_connection(self):
        """
        Ensure Redis connection is established.
        
        Uses lazy initialization to create the Redis client only when needed.
        This allows the backend to be created during application startup
        without immediately establishing the connection.
        """
        if self.redis is None:
            try:
                self.redis = aioredis.from_url(
                    self.url, 
                    decode_responses=True,
                    **self.connection_kwargs
                )
                logger.info(f"Redis connection initialized: {self.url}")
            except Exception as e:
                logger.error(f"Failed to establish Redis connection: {e}")
                raise
    
    async def get(self, key: str) -> Optional[str]:
        """
        Retrieve a value from Redis.
        
        Parameters
        ----------
        key : str
            The cache key to retrieve
            
        Returns
        -------
        Optional[str]
            The cached value if found, None otherwise or on error
        """
        try:
            await self._ensure_connection()
            return await self.redis.get(key)
        except Exception as e:
            logger.error(f"Redis GET error for key {key}: {e}")
            return None
    
    async def set(self, key: str, value: str, timeout: int) -> None:
        """
        Store a value in Redis with expiration.
        
        Parameters
        ----------
        key : str
            The cache key
        value : str
            The value to cache
        timeout : int
            Expiration timeout in seconds
        """
        try:
            await self._ensure_connection()
            if timeout <= 0:
                # Zero or negative timeout means no expiration
                await self.redis.set(key, value)
            else:
                await self.redis.setex(key, timeout, value)
        except Exception as e:
            logger.error(f"Redis SET error for key {key}: {e}")
    
    async def delete(self, key: str) -> None:
        """
        Delete a key from Redis.
        
        Parameters
        ----------
        key : str
            The cache key to delete
        """
        try:
            await self._ensure_connection()
            await self.redis.delete(key)
        except Exception as e:
            logger.error(f"Redis DELETE error for key {key}: {e}")
    
    async def close(self) -> None:
        """
        Close the Redis connection and clean up resources.
        
        This method should be called during application shutdown
        to properly close the Redis connection pool.
        """
        if self.redis:
            try:
                await self.redis.close()
                await self.redis.wait_closed()
                self.redis = None
                logger.info("Redis connection closed")
            except Exception as e:
                logger.error(f"Error closing Redis connection: {e}")
                self.redis = None  # Set to None anyway to prevent further use

    def __repr__(self) -> str:
        """Return string representation of RedisBackend."""
        return f"RedisBackend(url='{self.url}')"
