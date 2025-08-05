"""
Example of a custom Memcached backend implementation
"""
try:
    import aiomcache
except ImportError:
    raise ImportError(
        "Memcached backend requires 'aiomcache'. "
        "Install with: pip install cache-middleware[memcached]"
    )

from typing import Optional
from cache_middleware.backends import CacheBackend
from cache_middleware.logger_config import logger

# Note: This would require aiomcache or similar library
# pip install aiomcache


class MemcachedBackend(CacheBackend):
    """Memcached cache backend (example implementation)"""
    
    def __init__(self, host: str = "localhost", port: int = 11211, **kwargs):
        self.host = host
        self.port = port
        self.connection_kwargs = kwargs
        self.client = None
        logger.info(f"Memcached backend configured for {host}:{port}")
    
    async def _ensure_connection(self):
        """Lazy connection initialization"""
        if self.client is None:
            # This would require: import aiomcache
            # self.client = aiomcache.Client(self.host, self.port, **self.connection_kwargs)
            logger.info(f"Memcached connection initialized: {self.host}:{self.port}")
            raise NotImplementedError("Memcached backend requires aiomcache library")
    
    async def get(self, key: str) -> Optional[str]:
        await self._ensure_connection()
        try:
            # return await self.client.get(key.encode())
            return None
        except Exception as e:
            logger.error(f"Memcached GET error for key {key}: {e}")
            return None
    
    async def set(self, key: str, value: str, timeout: int) -> None:
        await self._ensure_connection()
        try:
            # await self.client.set(key.encode(), value.encode(), exptime=timeout)
            pass
        except Exception as e:
            logger.error(f"Memcached SET error for key {key}: {e}")
    
    async def delete(self, key: str) -> None:
        await self._ensure_connection()
        try:
            # await self.client.delete(key.encode())
            pass
        except Exception as e:
            logger.error(f"Memcached DELETE error for key {key}: {e}")
    
    async def close(self) -> None:
        if self.client:
            # await self.client.close()
            logger.info("Memcached connection closed")


# Para registrar el nuevo backend:
# from cache_middleware.backends.factory import CacheBackendFactory
# CacheBackendFactory.register_backend("memcached", MemcachedBackend)
