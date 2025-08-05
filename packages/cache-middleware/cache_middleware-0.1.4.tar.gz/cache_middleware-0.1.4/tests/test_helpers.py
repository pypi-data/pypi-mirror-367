"""
Tests for helper functions module.
"""
import pytest
import os
from unittest.mock import patch, Mock
from cache_middleware.helpers import (
    create_redis_backend_from_env,
    create_memory_backend_from_env,
    auto_configure_backend,
    create_production_redis_backend,
    create_development_backend,
    get_backend_for_environment
)
from cache_middleware.backends.redis_backend import RedisBackend
from cache_middleware.backends.memory_backend import MemoryBackend


class TestCreateRedisBackendFromEnv:
    """Test cases for create_redis_backend_from_env function."""
    
    @patch.dict(os.environ, {}, clear=True)
    def test_create_redis_backend_default_values(self):
        """Test creating Redis backend with default environment values."""
        backend = create_redis_backend_from_env()
        
        assert isinstance(backend, RedisBackend)
        assert backend.url == "redis://localhost:6379"
        assert backend.connection_kwargs.get("max_connections") == 10
        assert backend.connection_kwargs.get("password") is None
        assert backend.connection_kwargs.get("retry_on_timeout") is True
    
    @patch.dict(os.environ, {
        "REDIS_URL": "redis://custom-host:6380",
        "REDIS_MAX_CONNECTIONS": "20",
        "REDIS_PASSWORD": "secret",
        "REDIS_RETRY_ON_TIMEOUT": "false"
    })
    def test_create_redis_backend_custom_values(self):
        """Test creating Redis backend with custom environment values."""
        backend = create_redis_backend_from_env()
        
        assert isinstance(backend, RedisBackend)
        assert backend.url == "redis://custom-host:6380"
        assert backend.connection_kwargs.get("max_connections") == 20
        assert backend.connection_kwargs.get("password") == "secret"
        assert backend.connection_kwargs.get("retry_on_timeout") is False
    
    @patch.dict(os.environ, {"REDIS_MAX_CONNECTIONS": "invalid"})
    def test_create_redis_backend_invalid_max_connections(self):
        """Test creating Redis backend with invalid max_connections value."""
        with pytest.raises(ValueError):
            create_redis_backend_from_env()
    
    @patch.dict(os.environ, {"REDIS_RETRY_ON_TIMEOUT": "yes"})
    def test_create_redis_backend_retry_on_timeout_truthy(self):
        """Test Redis backend with truthy retry_on_timeout value."""
        backend = create_redis_backend_from_env()
        
        assert backend.connection_kwargs.get("retry_on_timeout") is False  # "yes" != "true"
    
    @patch.dict(os.environ, {"REDIS_RETRY_ON_TIMEOUT": "TRUE"})
    def test_create_redis_backend_retry_on_timeout_case_insensitive(self):
        """Test Redis backend with case-insensitive true value."""
        backend = create_redis_backend_from_env()
        
        assert backend.connection_kwargs.get("retry_on_timeout") is True
    
    @patch.dict(os.environ, {"REDIS_PASSWORD": ""})
    def test_create_redis_backend_empty_password(self):
        """Test Redis backend with empty password."""
        backend = create_redis_backend_from_env()
        
        assert backend.connection_kwargs.get("password") == ""


class TestCreateMemoryBackendFromEnv:
    """Test cases for create_memory_backend_from_env function."""
    
    @patch.dict(os.environ, {}, clear=True)
    def test_create_memory_backend_default_values(self):
        """Test creating memory backend with default environment values."""
        backend = create_memory_backend_from_env()
        
        assert isinstance(backend, MemoryBackend)
        assert backend.max_size == 1000
    
    @patch.dict(os.environ, {"MEMORY_CACHE_SIZE": "500"})
    def test_create_memory_backend_custom_size(self):
        """Test creating memory backend with custom cache size."""
        backend = create_memory_backend_from_env()
        
        assert isinstance(backend, MemoryBackend)
        assert backend.max_size == 500
    
    @patch.dict(os.environ, {"MEMORY_CACHE_SIZE": "0"})
    def test_create_memory_backend_zero_size(self):
        """Test creating memory backend with zero cache size."""
        backend = create_memory_backend_from_env()
        
        assert isinstance(backend, MemoryBackend)
        assert backend.max_size == 0
    
    @patch.dict(os.environ, {"MEMORY_CACHE_SIZE": "invalid"})
    def test_create_memory_backend_invalid_size(self):
        """Test creating memory backend with invalid cache size."""
        with pytest.raises(ValueError):
            create_memory_backend_from_env()


class TestAutoConfigureBackend:
    """Test cases for auto_configure_backend function."""
    
    @patch.dict(os.environ, {}, clear=True)
    def test_auto_configure_backend_default_memory(self):
        """Test auto-configure backend defaults to memory."""
        backend = auto_configure_backend()
        
        assert isinstance(backend, MemoryBackend)
        assert backend.max_size == 1000
    
    @patch.dict(os.environ, {"CACHE_BACKEND": "redis"})
    def test_auto_configure_backend_redis(self):
        """Test auto-configure backend with Redis."""
        backend = auto_configure_backend()
        
        assert isinstance(backend, RedisBackend)
        assert backend.url == "redis://localhost:6379"
    
    @patch.dict(os.environ, {"CACHE_BACKEND": "memory"})
    def test_auto_configure_backend_memory(self):
        """Test auto-configure backend with memory."""
        backend = auto_configure_backend()
        
        assert isinstance(backend, MemoryBackend)
        assert backend.max_size == 1000
    
    @patch.dict(os.environ, {"CACHE_BACKEND": "REDIS"})
    def test_auto_configure_backend_case_insensitive(self):
        """Test auto-configure backend is case insensitive."""
        backend = auto_configure_backend()
        
        assert isinstance(backend, RedisBackend)
    
    @patch.dict(os.environ, {"CACHE_BACKEND": "unknown"})
    def test_auto_configure_backend_unknown_type(self):
        """Test auto-configure backend with unknown type raises error."""
        with pytest.raises(ValueError, match="Unknown backend type from env: unknown"):
            auto_configure_backend()
    
    @patch.dict(os.environ, {
        "CACHE_BACKEND": "redis",
        "REDIS_URL": "redis://env-host:6379",
        "REDIS_MAX_CONNECTIONS": "15"
    })
    def test_auto_configure_backend_redis_with_env_vars(self):
        """Test auto-configure Redis backend respects environment variables."""
        backend = auto_configure_backend()
        
        assert isinstance(backend, RedisBackend)
        assert backend.url == "redis://env-host:6379"
        assert backend.connection_kwargs.get("max_connections") == 15
    
    @patch.dict(os.environ, {
        "CACHE_BACKEND": "memory",
        "MEMORY_CACHE_SIZE": "750"
    })
    def test_auto_configure_backend_memory_with_env_vars(self):
        """Test auto-configure memory backend respects environment variables."""
        backend = auto_configure_backend()
        
        assert isinstance(backend, MemoryBackend)
        assert backend.max_size == 750


class TestCreateProductionRedisBackend:
    """Test cases for create_production_redis_backend function."""
    
    @patch.dict(os.environ, {}, clear=True)
    def test_create_production_redis_backend_default(self):
        """Test creating production Redis backend with default URL."""
        backend = create_production_redis_backend()
        
        assert isinstance(backend, RedisBackend)
        assert backend.url == "redis://localhost:6379"
        assert backend.connection_kwargs.get("max_connections") == 100
        assert backend.connection_kwargs.get("retry_on_timeout") is True
        assert backend.connection_kwargs.get("socket_keepalive") is True
        assert backend.connection_kwargs.get("health_check_interval") == 30
        
        # Check keepalive options
        keepalive_options = backend.connection_kwargs.get("socket_keepalive_options")
        assert keepalive_options == {1: 1, 2: 3, 3: 5}
    
    @patch.dict(os.environ, {"REDIS_URL": "redis://prod-server:6380"})
    def test_create_production_redis_backend_custom_url(self):
        """Test creating production Redis backend with custom URL."""
        backend = create_production_redis_backend()
        
        assert isinstance(backend, RedisBackend)
        assert backend.url == "redis://prod-server:6380"
        # Other production settings should remain the same
        assert backend.connection_kwargs.get("max_connections") == 100


class TestCreateDevelopmentBackend:
    """Test cases for create_development_backend function."""
    
    def test_create_development_backend(self):
        """Test creating development backend."""
        backend = create_development_backend()
        
        assert isinstance(backend, MemoryBackend)
        assert backend.max_size == 500


class TestGetBackendForEnvironment:
    """Test cases for get_backend_for_environment function."""
    
    def test_get_backend_for_environment_production(self):
        """Test getting backend for production environment."""
        backend = get_backend_for_environment("production")
        
        assert isinstance(backend, RedisBackend)
        assert backend.connection_kwargs.get("max_connections") == 100
    
    def test_get_backend_for_environment_development(self):
        """Test getting backend for development environment."""
        backend = get_backend_for_environment("development")
        
        assert isinstance(backend, MemoryBackend)
        assert backend.max_size == 500
    
    def test_get_backend_for_environment_testing(self):
        """Test getting backend for testing environment."""
        backend = get_backend_for_environment("testing")
        
        assert isinstance(backend, MemoryBackend)
        assert backend.max_size == 100
    
    def test_get_backend_for_environment_unknown(self):
        """Test getting backend for unknown environment falls back to auto-configure."""
        with patch('cache_middleware.helpers.auto_configure_backend') as mock_auto:
            mock_backend = Mock()
            mock_auto.return_value = mock_backend
            
            result = get_backend_for_environment("unknown")
            
            assert result is mock_backend
            mock_auto.assert_called_once()
    
    @patch.dict(os.environ, {}, clear=True)
    def test_get_backend_for_environment_none_default(self):
        """Test getting backend with None env defaults to development."""
        backend = get_backend_for_environment(None)
        
        assert isinstance(backend, MemoryBackend)
        assert backend.max_size == 500
    
    @patch.dict(os.environ, {"ENVIRONMENT": "production"})
    def test_get_backend_for_environment_none_from_env(self):
        """Test getting backend with None env reads from environment variable."""
        backend = get_backend_for_environment(None)
        
        assert isinstance(backend, RedisBackend)
        assert backend.connection_kwargs.get("max_connections") == 100
    
    @patch.dict(os.environ, {"ENVIRONMENT": "TESTING"})
    def test_get_backend_for_environment_case_insensitive(self):
        """Test environment name is case insensitive."""
        backend = get_backend_for_environment(None)
        
        assert isinstance(backend, MemoryBackend)
        assert backend.max_size == 100
    
    def test_get_backend_for_environment_explicit_overrides_env(self):
        """Test explicit environment parameter overrides environment variable."""
        with patch.dict(os.environ, {"ENVIRONMENT": "production"}):
            backend = get_backend_for_environment("development")
            
            assert isinstance(backend, MemoryBackend)
            assert backend.max_size == 500
    
    @patch.dict(os.environ, {"ENVIRONMENT": "production", "REDIS_URL": "redis://env-redis:6379"})
    def test_get_backend_for_environment_production_with_env_vars(self):
        """Test production environment respects environment variables."""
        backend = get_backend_for_environment(None)
        
        assert isinstance(backend, RedisBackend)
        assert backend.url == "redis://env-redis:6379"


class TestHelperFunctionsIntegration:
    """Integration tests for helper functions."""
    
    @patch.dict(os.environ, {
        "CACHE_BACKEND": "redis",
        "REDIS_URL": "redis://integration-test:6379",
        "REDIS_MAX_CONNECTIONS": "25",
        "REDIS_PASSWORD": "integration-password"
    })
    def test_full_redis_configuration_integration(self):
        """Test full Redis configuration integration."""
        backend = auto_configure_backend()
        
        assert isinstance(backend, RedisBackend)
        assert backend.url == "redis://integration-test:6379"
        assert backend.connection_kwargs.get("max_connections") == 25
        assert backend.connection_kwargs.get("password") == "integration-password"
    
    @patch.dict(os.environ, {
        "ENVIRONMENT": "development",
        "MEMORY_CACHE_SIZE": "200"
    })
    def test_environment_specific_memory_configuration(self):
        """Test environment-specific memory configuration."""
        # Environment function should ignore MEMORY_CACHE_SIZE for development
        backend = get_backend_for_environment(None)
        
        assert isinstance(backend, MemoryBackend)
        assert backend.max_size == 500  # Development default, not env var
    
    def test_different_environment_backends(self):
        """Test that different environments return appropriate backends."""
        environments = ["production", "development", "testing"]
        backends = [get_backend_for_environment(env) for env in environments]
        
        # Production should be Redis
        assert isinstance(backends[0], RedisBackend)
        
        # Development should be Memory with 500 size
        assert isinstance(backends[1], MemoryBackend)
        assert backends[1].max_size == 500
        
        # Testing should be Memory with 100 size
        assert isinstance(backends[2], MemoryBackend)
        assert backends[2].max_size == 100
