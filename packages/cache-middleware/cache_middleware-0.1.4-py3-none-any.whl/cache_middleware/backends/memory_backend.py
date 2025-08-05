"""
In-memory cache backend implementation.

This module provides a simple in-memory cache backend suitable for
development, testing, and single-instance deployments where Redis
is not available or needed.
"""
import time
from typing import Optional, Dict, Tuple
from cache_middleware.backends import CacheBackend
from cache_middleware.logger_config import logger


class MemoryBackend(CacheBackend):
    """
    In-memory cache backend for development and testing.
    
    This backend stores cache entries in memory using a Python dictionary.
    It includes automatic expiration of entries and simple LRU eviction
    when the cache reaches its maximum size.
    
    Parameters
    ----------
    max_size : int, default=1000
        Maximum number of entries to store in the cache
        
    Attributes
    ----------
    max_size : int
        Maximum cache size
    _cache : Dict[str, Tuple[str, float]]
        Internal cache storage mapping keys to (value, expiry_time) tuples
        
    Examples
    --------
    >>> backend = MemoryBackend(max_size=500)
    >>> await backend.set("key1", "value1", 300)
    >>> value = await backend.get("key1")
    """
    
    def __init__(self, max_size: int = 1000):
        """
        Initialize the in-memory cache backend.
        
        Parameters
        ----------
        max_size : int, default=1000
            Maximum number of cache entries to store
        """
        self.max_size = max_size
        self._cache: Dict[str, Tuple[str, float]] = {}  # key -> (value, expiry_time)
        logger.info(f"In-memory cache initialized with max_size={max_size}")
    
    def _cleanup_expired(self):
        """
        Remove expired entries from the cache.
        
        This method is called before each get/set operation to ensure
        expired entries are cleaned up automatically.
        """
        current_time = time.time()
        expired_keys = [
            key for key, (_, expiry) in self._cache.items() 
            if expiry < current_time
        ]
        for key in expired_keys:
            del self._cache[key]
    
    def _evict_if_needed(self):
        """
        Evict oldest entries if cache has reached maximum size.
        
        Uses a simple FIFO (First In, First Out) eviction strategy
        by removing the first entry in the dictionary.
        """
        if self.max_size <= 0:
            # If max_size is 0 or negative, clear all entries
            self._cache.clear()
            return
            
        while len(self._cache) >= self.max_size:
            if not self._cache:  # Safety check for empty cache
                break
            # Simple FIFO: remove oldest entry (first in dict order)
            oldest_key = next(iter(self._cache))
            del self._cache[oldest_key]
    
    async def get(self, key: str) -> Optional[str]:
        """
        Retrieve a value from the cache.
        
        Parameters
        ----------
        key : str
            The cache key to retrieve
            
        Returns
        -------
        Optional[str]
            The cached value if found and not expired, None otherwise
        """
        self._cleanup_expired()
        if key in self._cache:
            value, expiry = self._cache[key]
            if expiry > time.time():
                return value
            else:
                del self._cache[key]
        return None
    
    async def set(self, key: str, value: str, timeout: int) -> None:
        """
        Store a value in the cache with expiration.
        
        Parameters
        ----------
        key : str
            The cache key
        value : str
            The value to cache
        timeout : int
            Expiration timeout in seconds
        """
        # If max_size is 0, don't store anything
        if self.max_size == 0:
            logger.debug(f"Not storing key '{key}' because max_size=0")
            return
            
        self._cleanup_expired()
        self._evict_if_needed()
        expiry_time = time.time() + timeout
        self._cache[key] = (value, expiry_time)
        logger.debug(f"Stored key '{key}' in memory cache with timeout {timeout}s")
    
    async def delete(self, key: str) -> None:
        """
        Delete a key from the cache.
        
        Parameters
        ----------
        key : str
            The cache key to delete
        """
        self._cache.pop(key, None)
    
    async def close(self) -> None:
        """
        Close the cache backend and clean up resources.
        
        For the in-memory backend, this clears all cached entries.
        """
        self._cache.clear()
        logger.info("In-memory cache cleared")
    
    def __repr__(self) -> str:
        """Return string representation of MemoryBackend."""
        return f"MemoryBackend(max_size={self.max_size}, current_entries={len(self._cache)})"
