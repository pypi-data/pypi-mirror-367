"""
Tests for memory cache backend.
"""
import pytest
import asyncio
import time
from unittest.mock import patch, Mock
from cache_middleware.backends.memory_backend import MemoryBackend


class TestMemoryBackend:
    """Test cases for MemoryBackend."""
    
    def test_memory_backend_initialization_default(self):
        """Test MemoryBackend initialization with default parameters."""
        backend = MemoryBackend()
        
        assert backend.max_size == 1000
        assert backend._cache == {}
    
    def test_memory_backend_initialization_custom_size(self):
        """Test MemoryBackend initialization with custom max_size."""
        custom_size = 500
        backend = MemoryBackend(max_size=custom_size)
        
        assert backend.max_size == custom_size
        assert backend._cache == {}
    
    def test_memory_backend_initialization_zero_size(self):
        """Test MemoryBackend initialization with zero max_size."""
        backend = MemoryBackend(max_size=0)
        
        assert backend.max_size == 0
        assert backend._cache == {}
    
    def test_memory_backend_initialization_negative_size(self):
        """Test MemoryBackend initialization with negative max_size."""
        backend = MemoryBackend(max_size=-1)
        
        assert backend.max_size == -1
        assert backend._cache == {}
    
    @pytest.mark.asyncio
    async def test_set_and_get_basic(self):
        """Test basic set and get operations."""
        backend = MemoryBackend()
        
        key = "test_key"
        value = "test_value"
        timeout = 300
        
        await backend.set(key, value, timeout)
        result = await backend.get(key)
        
        assert result == value
    
    @pytest.mark.asyncio
    async def test_get_nonexistent_key(self):
        """Test getting a non-existent key returns None."""
        backend = MemoryBackend()
        
        result = await backend.get("nonexistent_key")
        
        assert result is None
    
    @pytest.mark.asyncio
    async def test_set_overwrite_existing_key(self):
        """Test overwriting an existing key."""
        backend = MemoryBackend()
        
        key = "test_key"
        original_value = "original_value"
        new_value = "new_value"
        timeout = 300
        
        await backend.set(key, original_value, timeout)
        await backend.set(key, new_value, timeout)
        result = await backend.get(key)
        
        assert result == new_value
    
    @pytest.mark.asyncio
    async def test_expiration(self):
        """Test that entries expire correctly."""
        backend = MemoryBackend()
        
        key = "expire_key"
        value = "expire_value"
        timeout = 1  # 1 second
        
        await backend.set(key, value, timeout)
        
        # Should exist immediately
        result = await backend.get(key)
        assert result == value
        
        # Wait for expiration
        await asyncio.sleep(1.1)
        
        # Should be expired
        result = await backend.get(key)
        assert result is None
        
        # Key should be removed from cache
        assert key not in backend._cache
    
    @pytest.mark.asyncio
    async def test_delete_existing_key(self):
        """Test deleting an existing key."""
        backend = MemoryBackend()
        
        key = "delete_key"
        value = "delete_value"
        timeout = 300
        
        await backend.set(key, value, timeout)
        await backend.delete(key)
        result = await backend.get(key)
        
        assert result is None
        assert key not in backend._cache
    
    @pytest.mark.asyncio
    async def test_delete_nonexistent_key(self):
        """Test deleting a non-existent key doesn't raise error."""
        backend = MemoryBackend()
        
        # Should not raise an exception
        await backend.delete("nonexistent_key")
    
    @pytest.mark.asyncio
    async def test_close(self):
        """Test close method clears cache."""
        backend = MemoryBackend()
        
        # Add some data
        await backend.set("key1", "value1", 300)
        await backend.set("key2", "value2", 300)
        
        assert len(backend._cache) == 2
        
        await backend.close()
        
        assert len(backend._cache) == 0
    
    @pytest.mark.asyncio
    async def test_lru_eviction(self):
        """Test LRU eviction when max_size is reached."""
        max_size = 3
        backend = MemoryBackend(max_size=max_size)
        
        # Fill cache to max_size
        for i in range(max_size):
            await backend.set(f"key_{i}", f"value_{i}", 300)
        
        assert len(backend._cache) == max_size
        
        # Access key_1 to make it recently used
        await backend.get("key_1")
        
        # Add one more item, should evict least recently used (key_0)
        await backend.set("key_new", "value_new", 300)
        
        assert len(backend._cache) == max_size
        assert await backend.get("key_0") is None  # Should be evicted
        assert await backend.get("key_1") == "value_1"  # Should still exist
        assert await backend.get("key_2") == "value_2"  # Should still exist
        assert await backend.get("key_new") == "value_new"  # Should exist
    
    @pytest.mark.asyncio
    async def test_zero_max_size_behavior(self):
        """Test behavior with zero max_size."""
        backend = MemoryBackend(max_size=0)
        
        # Should not store anything
        await backend.set("key", "value", 300)
        result = await backend.get("key")
        
        assert result is None
        assert len(backend._cache) == 0
    
    @pytest.mark.asyncio
    async def test_negative_timeout(self):
        """Test behavior with negative timeout."""
        backend = MemoryBackend()
        
        key = "negative_timeout_key"
        value = "negative_timeout_value"
        timeout = -1
        
        await backend.set(key, value, timeout)
        
        # Should be immediately expired
        result = await backend.get(key)
        assert result is None
    
    @pytest.mark.asyncio
    async def test_zero_timeout(self):
        """Test behavior with zero timeout."""
        backend = MemoryBackend()
        
        key = "zero_timeout_key"
        value = "zero_timeout_value"
        timeout = 0
        
        await backend.set(key, value, timeout)
        
        # Should be immediately expired
        result = await backend.get(key)
        assert result is None
    
    @pytest.mark.asyncio
    async def test_concurrent_access(self):
        """Test concurrent access to cache."""
        backend = MemoryBackend()
        
        async def set_operation(i):
            await backend.set(f"key_{i}", f"value_{i}", 300)
        
        async def get_operation(i):
            return await backend.get(f"key_{i}")
        
        # Set values concurrently
        await asyncio.gather(*[set_operation(i) for i in range(10)])
        
        # Get values concurrently
        results = await asyncio.gather(*[get_operation(i) for i in range(10)])
        
        # Verify all values were set and retrieved correctly
        for i, result in enumerate(results):
            assert result == f"value_{i}"
    
    @pytest.mark.asyncio
    async def test_large_values(self):
        """Test storing large values."""
        backend = MemoryBackend()
        
        key = "large_value_key"
        large_value = "x" * 100000  # 100KB string
        timeout = 300
        
        await backend.set(key, large_value, timeout)
        result = await backend.get(key)
        
        assert result == large_value
    
    @pytest.mark.asyncio
    async def test_special_characters_in_keys(self):
        """Test keys with special characters."""
        backend = MemoryBackend()
        
        special_keys = [
            "key with spaces",
            "key:with:colons",
            "key/with/slashes",
            "key-with-dashes",
            "key_with_underscores",
            "key.with.dots",
            "key@with@symbols",
            "key#with#hash",
            "用户名",  # Unicode characters
            "🔑",  # Emoji
        ]
        
        for key in special_keys:
            value = f"value_for_{key}"
            await backend.set(key, value, 300)
            result = await backend.get(key)
            assert result == value
    
    @pytest.mark.asyncio
    async def test_empty_values(self):
        """Test storing empty values."""
        backend = MemoryBackend()
        
        test_cases = [
            ("empty_string", ""),
            ("json_null", "null"),
            ("json_empty_object", "{}"),
            ("json_empty_array", "[]"),
            ("whitespace", "   "),
        ]
        
        for key, value in test_cases:
            await backend.set(key, value, 300)
            result = await backend.get(key)
            assert result == value
    
    @pytest.mark.asyncio
    async def test_cleanup_expired_entries_on_get(self):
        """Test that expired entries are cleaned up during get operations."""
        backend = MemoryBackend()
        
        # Set entries with different expiration times
        await backend.set("key1", "value1", 1)  # Expires in 1 second
        await backend.set("key2", "value2", 300)  # Expires in 5 minutes
        
        assert len(backend._cache) == 2
        
        # Wait for first key to expire
        await asyncio.sleep(1.1)
        
        # Access the second key, should clean up the first
        result = await backend.get("key2")
        assert result == "value2"
        
        # First key should be removed during the get operation
        assert "key1" not in backend._cache
        assert "key2" in backend._cache
    
    @pytest.mark.asyncio
    @patch('cache_middleware.backends.memory_backend.logger')
    async def test_logging_behavior(self, mock_logger):
        """Test that operations are logged correctly."""
        backend = MemoryBackend()
        
        # Test set operation logging
        await backend.set("test_key", "test_value", 300)
        mock_logger.debug.assert_called()
        
        # Test get operation logging
        await backend.get("test_key")
        mock_logger.debug.assert_called()
        
        # Test delete operation logging
        await backend.delete("test_key")
        mock_logger.debug.assert_called()
    
    @pytest.mark.asyncio
    async def test_memory_backend_as_context_manager(self):
        """Test using MemoryBackend in async context manager pattern."""
        backend = MemoryBackend()
        
        try:
            await backend.set("test_key", "test_value", 300)
            result = await backend.get("test_key")
            assert result == "test_value"
        finally:
            await backend.close()
            
        # After close, cache should be empty
        assert len(backend._cache) == 0
    
    def test_memory_backend_repr(self):
        """Test string representation of MemoryBackend."""
        backend = MemoryBackend(max_size=500)
        repr_str = repr(backend)
        
        assert "MemoryBackend" in repr_str
        assert "500" in repr_str or "max_size" in repr_str
