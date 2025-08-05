"""
Tests for Redis cache backend.
"""
import pytest
import asyncio
from unittest.mock import AsyncMock, Mock, patch, MagicMock
from cache_middleware.backends.redis_backend import RedisBackend


class TestRedisBackend:
    """Test cases for RedisBackend."""
    
    def test_redis_backend_initialization_default(self):
        """Test RedisBackend initialization with default parameters."""
        backend = RedisBackend()
        
        assert backend.url == "redis://localhost:6379"
        assert backend.connection_kwargs == {}
        assert backend.redis is None
    
    def test_redis_backend_initialization_custom_url(self):
        """Test RedisBackend initialization with custom URL."""
        custom_url = "redis://custom-host:6380/1"
        backend = RedisBackend(url=custom_url)
        
        assert backend.url == custom_url
        assert backend.connection_kwargs == {}
        assert backend.redis is None
    
    def test_redis_backend_initialization_with_kwargs(self):
        """Test RedisBackend initialization with additional kwargs."""
        url = "redis://localhost:6379"
        kwargs = {
            "max_connections": 20,
            "retry_on_timeout": True,
            "password": "secret"
        }
        backend = RedisBackend(url=url, **kwargs)
        
        assert backend.url == url
        assert backend.connection_kwargs == kwargs
        assert backend.redis is None
    
    @pytest.mark.asyncio
    @patch('cache_middleware.backends.redis_backend.aioredis')
    async def test_lazy_connection_initialization(self, mock_aioredis):
        """Test that Redis connection is initialized lazily."""
        mock_redis = AsyncMock()
        mock_aioredis.from_url.return_value = mock_redis
        
        backend = RedisBackend()
        
        # Connection should not be created yet
        assert backend.redis is None
        mock_aioredis.from_url.assert_not_called()
        
        # First operation should create connection
        await backend.get("test_key")
        
        mock_aioredis.from_url.assert_called_once_with(
            backend.url,
            decode_responses=True,
            **backend.connection_kwargs
        )
        assert backend.redis is mock_redis
    
    @pytest.mark.asyncio
    @patch('cache_middleware.backends.redis_backend.aioredis')
    async def test_get_existing_key(self, mock_aioredis):
        """Test getting an existing key from Redis."""
        mock_redis = AsyncMock()
        mock_redis.get.return_value = "test_value"
        mock_aioredis.from_url.return_value = mock_redis
        
        backend = RedisBackend()
        result = await backend.get("test_key")
        
        assert result == "test_value"
        mock_redis.get.assert_called_once_with("test_key")
    
    @pytest.mark.asyncio
    @patch('cache_middleware.backends.redis_backend.aioredis')
    async def test_get_nonexistent_key(self, mock_aioredis):
        """Test getting a non-existent key returns None."""
        mock_redis = AsyncMock()
        mock_redis.get.return_value = None
        mock_aioredis.from_url.return_value = mock_redis
        
        backend = RedisBackend()
        result = await backend.get("nonexistent_key")
        
        assert result is None
        mock_redis.get.assert_called_once_with("nonexistent_key")
    
    @pytest.mark.asyncio
    @patch('cache_middleware.backends.redis_backend.aioredis')
    async def test_set_with_timeout(self, mock_aioredis):
        """Test setting a key with timeout."""
        mock_redis = AsyncMock()
        mock_aioredis.from_url.return_value = mock_redis
        
        backend = RedisBackend()
        await backend.set("test_key", "test_value", 300)
        
        mock_redis.setex.assert_called_once_with("test_key", 300, "test_value")
    
    @pytest.mark.asyncio
    @patch('cache_middleware.backends.redis_backend.aioredis')
    async def test_set_with_zero_timeout(self, mock_aioredis):
        """Test setting a key with zero timeout."""
        mock_redis = AsyncMock()
        mock_aioredis.from_url.return_value = mock_redis
        
        backend = RedisBackend()
        await backend.set("test_key", "test_value", 0)
        
        # Zero timeout should use set without expiration
        mock_redis.set.assert_called_once_with("test_key", "test_value")
    
    @pytest.mark.asyncio
    @patch('cache_middleware.backends.redis_backend.aioredis')
    async def test_set_with_negative_timeout(self, mock_aioredis):
        """Test setting a key with negative timeout."""
        mock_redis = AsyncMock()
        mock_aioredis.from_url.return_value = mock_redis
        
        backend = RedisBackend()
        await backend.set("test_key", "test_value", -1)
        
        # Negative timeout should use set without expiration
        mock_redis.set.assert_called_once_with("test_key", "test_value")
    
    @pytest.mark.asyncio
    @patch('cache_middleware.backends.redis_backend.aioredis')
    async def test_delete_existing_key(self, mock_aioredis):
        """Test deleting an existing key."""
        mock_redis = AsyncMock()
        mock_aioredis.from_url.return_value = mock_redis
        
        backend = RedisBackend()
        await backend.delete("test_key")
        
        mock_redis.delete.assert_called_once_with("test_key")
    
    @pytest.mark.asyncio
    @patch('cache_middleware.backends.redis_backend.aioredis')
    async def test_close_connection(self, mock_aioredis):
        """Test closing Redis connection."""
        mock_redis = AsyncMock()
        mock_aioredis.from_url.return_value = mock_redis
        
        backend = RedisBackend()
        
        # Initialize connection
        await backend.get("test_key")
        assert backend.redis is not None
        
        # Close connection
        await backend.close()
        
        mock_redis.close.assert_called_once()
        mock_redis.wait_closed.assert_called_once()
        assert backend.redis is None
    
    @pytest.mark.asyncio
    @patch('cache_middleware.backends.redis_backend.aioredis')
    async def test_close_without_connection(self, mock_aioredis):
        """Test closing when no connection exists."""
        backend = RedisBackend()
        
        # Should not raise an exception
        await backend.close()
        
        assert backend.redis is None
    
    @pytest.mark.asyncio
    @patch('cache_middleware.backends.redis_backend.aioredis')
    @patch('cache_middleware.backends.redis_backend.logger')
    async def test_get_redis_connection_error(self, mock_logger, mock_aioredis):
        """Test handling Redis connection errors during get."""
        mock_aioredis.from_url.side_effect = Exception("Connection failed")
        
        backend = RedisBackend()
        result = await backend.get("test_key")
        
        assert result is None
        mock_logger.error.assert_called()
    
    @pytest.mark.asyncio
    @patch('cache_middleware.backends.redis_backend.aioredis')
    @patch('cache_middleware.backends.redis_backend.logger')
    async def test_get_redis_operation_error(self, mock_logger, mock_aioredis):
        """Test handling Redis operation errors during get."""
        mock_redis = AsyncMock()
        mock_redis.get.side_effect = Exception("Operation failed")
        mock_aioredis.from_url.return_value = mock_redis
        
        backend = RedisBackend()
        result = await backend.get("test_key")
        
        assert result is None
        mock_logger.error.assert_called()
    
    @pytest.mark.asyncio
    @patch('cache_middleware.backends.redis_backend.aioredis')
    @patch('cache_middleware.backends.redis_backend.logger')
    async def test_set_redis_connection_error(self, mock_logger, mock_aioredis):
        """Test handling Redis connection errors during set."""
        mock_aioredis.from_url.side_effect = Exception("Connection failed")
        
        backend = RedisBackend()
        
        # Should not raise exception
        await backend.set("test_key", "test_value", 300)
        
        mock_logger.error.assert_called()
    
    @pytest.mark.asyncio
    @patch('cache_middleware.backends.redis_backend.aioredis')
    @patch('cache_middleware.backends.redis_backend.logger')
    async def test_set_redis_operation_error(self, mock_logger, mock_aioredis):
        """Test handling Redis operation errors during set."""
        mock_redis = AsyncMock()
        mock_redis.setex.side_effect = Exception("Operation failed")
        mock_aioredis.from_url.return_value = mock_redis
        
        backend = RedisBackend()
        
        # Should not raise exception
        await backend.set("test_key", "test_value", 300)
        
        mock_logger.error.assert_called()
    
    @pytest.mark.asyncio
    @patch('cache_middleware.backends.redis_backend.aioredis')
    @patch('cache_middleware.backends.redis_backend.logger')
    async def test_delete_redis_connection_error(self, mock_logger, mock_aioredis):
        """Test handling Redis connection errors during delete."""
        mock_aioredis.from_url.side_effect = Exception("Connection failed")
        
        backend = RedisBackend()
        
        # Should not raise exception
        await backend.delete("test_key")
        
        mock_logger.error.assert_called()
    
    @pytest.mark.asyncio
    @patch('cache_middleware.backends.redis_backend.aioredis')
    @patch('cache_middleware.backends.redis_backend.logger')
    async def test_delete_redis_operation_error(self, mock_logger, mock_aioredis):
        """Test handling Redis operation errors during delete."""
        mock_redis = AsyncMock()
        mock_redis.delete.side_effect = Exception("Operation failed")
        mock_aioredis.from_url.return_value = mock_redis
        
        backend = RedisBackend()
        
        # Should not raise exception
        await backend.delete("test_key")
        
        mock_logger.error.assert_called()
    
    @pytest.mark.asyncio
    @patch('cache_middleware.backends.redis_backend.aioredis')
    async def test_concurrent_operations(self, mock_aioredis):
        """Test concurrent Redis operations."""
        mock_redis = AsyncMock()
        mock_redis.get.return_value = "test_value"
        mock_aioredis.from_url.return_value = mock_redis
        
        backend = RedisBackend()
        
        # Test concurrent get operations
        tasks = [backend.get(f"key_{i}") for i in range(10)]
        results = await asyncio.gather(*tasks)
        
        assert len(results) == 10
        assert all(result == "test_value" for result in results)
        assert mock_redis.get.call_count == 10
    
    @pytest.mark.asyncio
    @patch('cache_middleware.backends.redis_backend.aioredis')
    async def test_connection_reuse(self, mock_aioredis):
        """Test that Redis connection is reused across operations."""
        mock_redis = AsyncMock()
        mock_aioredis.from_url.return_value = mock_redis
        
        backend = RedisBackend()
        
        # Perform multiple operations
        await backend.get("key1")
        await backend.set("key2", "value2", 300)
        await backend.delete("key3")
        
        # Connection should be created only once
        mock_aioredis.from_url.assert_called_once()
        assert backend.redis is mock_redis
    
    @pytest.mark.asyncio
    @patch('cache_middleware.backends.redis_backend.aioredis')
    async def test_different_redis_urls(self, mock_aioredis):
        """Test RedisBackend with different URL formats."""
        mock_redis = AsyncMock()
        mock_aioredis.from_url.return_value = mock_redis
        
        test_urls = [
            "redis://localhost:6379",
            "redis://localhost:6379/0",
            "redis://localhost:6379/1",
            "redis://:password@localhost:6379",
            "redis://user:password@localhost:6379",
            "redis://localhost:6380",
            "rediss://localhost:6380",  # SSL
        ]
        
        for url in test_urls:
            backend = RedisBackend(url=url)
            await backend.get("test_key")
            
            # Verify correct URL was used
            mock_aioredis.from_url.assert_called_with(
                url,
                decode_responses=True
            )
            mock_aioredis.from_url.reset_mock()
    
    @pytest.mark.asyncio
    @patch('cache_middleware.backends.redis_backend.aioredis')
    async def test_redis_backend_with_connection_kwargs(self, mock_aioredis):
        """Test RedisBackend with various connection parameters."""
        mock_redis = AsyncMock()
        mock_aioredis.from_url.return_value = mock_redis
        
        kwargs = {
            "max_connections": 20,
            "retry_on_timeout": True,
            "socket_keepalive": True,
            "socket_keepalive_options": {1: 1, 2: 3, 3: 5},
            "health_check_interval": 30,
            "password": "secret",
            "db": 1,
        }
        
        backend = RedisBackend(**kwargs)
        await backend.get("test_key")
        
        expected_kwargs = kwargs.copy()
        expected_kwargs["decode_responses"] = True
        
        mock_aioredis.from_url.assert_called_once_with(
            "redis://localhost:6379",
            **expected_kwargs
        )
    
    @pytest.mark.asyncio
    @patch('cache_middleware.backends.redis_backend.aioredis')
    async def test_large_values(self, mock_aioredis):
        """Test storing large values in Redis."""
        mock_redis = AsyncMock()
        mock_aioredis.from_url.return_value = mock_redis
        
        backend = RedisBackend()
        large_value = "x" * 100000  # 100KB string
        
        await backend.set("large_key", large_value, 300)
        
        mock_redis.setex.assert_called_once_with("large_key", 300, large_value)
    
    @pytest.mark.asyncio
    @patch('cache_middleware.backends.redis_backend.aioredis')
    async def test_special_characters_in_keys(self, mock_aioredis):
        """Test Redis backend with special characters in keys."""
        mock_redis = AsyncMock()
        mock_redis.get.return_value = "test_value"
        mock_aioredis.from_url.return_value = mock_redis
        
        backend = RedisBackend()
        
        special_keys = [
            "key with spaces",
            "key:with:colons",
            "key/with/slashes", 
            "key-with-dashes",
            "key_with_underscores",
            "key.with.dots",
            "用户名",  # Unicode
            "🔑",  # Emoji
        ]
        
        for key in special_keys:
            result = await backend.get(key)
            assert result == "test_value"
            mock_redis.get.assert_called_with(key)
    
    @pytest.mark.asyncio
    @patch('cache_middleware.backends.redis_backend.aioredis')
    @patch('cache_middleware.backends.redis_backend.logger')
    async def test_close_connection_error(self, mock_logger, mock_aioredis):
        """Test handling errors during connection close."""
        mock_redis = AsyncMock()
        mock_redis.close.side_effect = Exception("Close failed")
        mock_aioredis.from_url.return_value = mock_redis
        
        backend = RedisBackend()
        
        # Initialize connection
        await backend.get("test_key")
        
        # Close should handle exception gracefully
        await backend.close()
        
        mock_logger.error.assert_called()
        assert backend.redis is None
    
    def test_redis_backend_repr(self):
        """Test string representation of RedisBackend."""
        backend = RedisBackend(url="redis://test:6379")
        repr_str = repr(backend)
        
        assert "RedisBackend" in repr_str
        assert "redis://test:6379" in repr_str
    
    @pytest.mark.asyncio
    @patch('cache_middleware.backends.redis_backend.aioredis')
    async def test_redis_backend_as_context_manager(self, mock_aioredis):
        """Test using RedisBackend in async context manager pattern."""
        mock_redis = AsyncMock()
        mock_aioredis.from_url.return_value = mock_redis
        
        backend = RedisBackend()
        
        try:
            await backend.set("test_key", "test_value", 300)
            result = await backend.get("test_key")
            # In real scenario, result would be the value
        finally:
            await backend.close()
            
        mock_redis.close.assert_called_once()
        assert backend.redis is None
