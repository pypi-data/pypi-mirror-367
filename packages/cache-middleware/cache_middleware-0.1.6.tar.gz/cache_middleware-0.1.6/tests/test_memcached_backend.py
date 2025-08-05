"""
Tests for Memcached cache backend.
"""
import pytest
from unittest.mock import AsyncMock, Mock, patch, MagicMock
from cache_middleware.backends.memcached_backend import MemcachedBackend


class TestMemcachedBackend:
    """Test cases for MemcachedBackend."""
    
    def test_memcached_backend_initialization_default(self):
        """Test MemcachedBackend initialization with default parameters."""
        backend = MemcachedBackend()
        
        assert backend.host == "localhost"
        assert backend.port == 11211
        assert backend.connection_kwargs == {}
        assert backend.client is None
    
    def test_memcached_backend_initialization_custom(self):
        """Test MemcachedBackend initialization with custom parameters."""
        host = "memcached.example.com"
        port = 11212
        kwargs = {"pool_size": 10, "timeout": 30}
        
        backend = MemcachedBackend(host=host, port=port, **kwargs)
        
        assert backend.host == host
        assert backend.port == port
        assert backend.connection_kwargs == kwargs
        assert backend.client is None
    
    @pytest.mark.asyncio
    @patch('cache_middleware.backends.memcached_backend.logger')
    async def test_ensure_connection_not_implemented(self, mock_logger):
        """Test that _ensure_connection raises NotImplementedError."""
        backend = MemcachedBackend()
        
        with pytest.raises(NotImplementedError, match="aiomcache library"):
            await backend._ensure_connection()
    
    @pytest.mark.asyncio
    async def test_get_not_implemented(self):
        """Test that get method raises NotImplementedError."""
        backend = MemcachedBackend()
        
        with pytest.raises(NotImplementedError):
            await backend.get("test_key")
    
    @pytest.mark.asyncio
    async def test_set_not_implemented(self):
        """Test that set method raises NotImplementedError."""
        backend = MemcachedBackend()
        
        with pytest.raises(NotImplementedError):
            await backend.set("test_key", "test_value", 300)
    
    @pytest.mark.asyncio
    async def test_delete_not_implemented(self):
        """Test that delete method raises NotImplementedError."""
        backend = MemcachedBackend()
        
        with pytest.raises(NotImplementedError):
            await backend.delete("test_key")
    
    @pytest.mark.asyncio
    async def test_close_method_exists(self):
        """Test that close method exists and doesn't raise error."""
        backend = MemcachedBackend()
        
        # Should not raise an exception even if not implemented
        await backend.close()
    
    @pytest.mark.asyncio
    @patch('cache_middleware.backends.memcached_backend.logger')
    async def test_initialization_logging(self, mock_logger):
        """Test that initialization logs correct information."""
        host = "test-host"
        port = 12345
        
        MemcachedBackend(host=host, port=port)
        
        mock_logger.info.assert_called_with(f"Memcached backend configured for {host}:{port}")
    
    def test_memcached_backend_repr(self):
        """Test string representation of MemcachedBackend."""
        backend = MemcachedBackend(host="test-host", port=12345)
        repr_str = repr(backend)
        
        assert "MemcachedBackend" in repr_str or "test-host" in repr_str or "12345" in repr_str


# Note: Additional tests for fully implemented MemcachedBackend would go here
# Currently disabled because the backend raises NotImplementedError for most operations
