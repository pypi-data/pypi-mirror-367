"""
Cache backend interface and base classes.

This module defines the abstract base class that all cache backends
must implement. It provides a consistent interface for different
caching strategies (Redis, in-memory, etc.).
"""
from abc import ABC, abstractmethod
from typing import Optional


class CacheBackend(ABC):
    """
    Abstract base class for cache backends.
    
    This class defines the interface that all cache backends must implement.
    It ensures consistency across different caching strategies and makes
    it easy to swap backends without changing the middleware code.
    
    All methods are async to support both sync and async backend implementations.
    Backend implementations should handle their own connection management,
    error handling, and resource cleanup.
    """
    
    @abstractmethod
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
            
        Notes
        -----
        Implementations should:
        - Return None if the key doesn't exist
        - Return None if the key has expired
        - Handle connection errors gracefully
        - Use appropriate logging for debugging
        """
        pass
    
    @abstractmethod
    async def set(self, key: str, value: str, timeout: int) -> None:
        """
        Store a value in the cache with expiration.
        
        Parameters
        ----------
        key : str
            The cache key
        value : str
            The value to cache (typically JSON string)
        timeout : int
            Expiration timeout in seconds
            
        Notes
        -----
        Implementations should:
        - Overwrite existing keys
        - Set appropriate expiration
        - Handle storage errors gracefully
        - Use appropriate logging for debugging
        """
        pass
    
    @abstractmethod
    async def delete(self, key: str) -> None:
        """
        Delete a key from the cache.
        
        Parameters
        ----------
        key : str
            The cache key to delete
            
        Notes
        -----
        Implementations should:
        - Silently ignore non-existent keys
        - Handle deletion errors gracefully
        - Use appropriate logging for debugging
        """
        pass
    
    @abstractmethod
    async def close(self) -> None:
        """
        Close connections and clean up resources.
        
        This method should be called during application shutdown
        to properly clean up any resources (connections, files, etc.)
        used by the backend.
        
        Notes
        -----
        Implementations should:
        - Close any open connections
        - Clean up temporary resources
        - Be safe to call multiple times
        - Not raise exceptions on cleanup errors
        """
        pass


# Export the base class
__all__ = ["CacheBackend"]
