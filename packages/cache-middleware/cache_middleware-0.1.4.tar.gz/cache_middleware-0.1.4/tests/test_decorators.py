"""
Tests for cache decorators module.
"""
import pytest
from unittest.mock import Mock
from cache_middleware.decorators import cache


class TestCacheDecorator:
    """Test cases for the @cache decorator."""
    
    def test_cache_decorator_default_timeout(self):
        """Test cache decorator with default timeout."""
        @cache()
        def test_function():
            return {"data": "test"}
        
        assert hasattr(test_function, '_use_cache')
        assert test_function._use_cache is True
        assert hasattr(test_function, '_cache_timeout')
        assert test_function._cache_timeout == 300  # Default timeout
    
    def test_cache_decorator_custom_timeout(self):
        """Test cache decorator with custom timeout."""
        timeout_value = 600
        
        @cache(timeout=timeout_value)
        def test_function():
            return {"data": "test"}
        
        assert hasattr(test_function, '_use_cache')
        assert test_function._use_cache is True
        assert hasattr(test_function, '_cache_timeout')
        assert test_function._cache_timeout == timeout_value
    
    def test_cache_decorator_zero_timeout(self):
        """Test cache decorator with zero timeout."""
        @cache(timeout=0)
        def test_function():
            return {"data": "test"}
        
        assert hasattr(test_function, '_use_cache')
        assert test_function._use_cache is True
        assert hasattr(test_function, '_cache_timeout')
        assert test_function._cache_timeout == 0
    
    def test_cache_decorator_negative_timeout(self):
        """Test cache decorator with negative timeout."""
        @cache(timeout=-1)
        def test_function():
            return {"data": "test"}
        
        assert hasattr(test_function, '_use_cache')
        assert test_function._use_cache is True
        assert hasattr(test_function, '_cache_timeout')
        assert test_function._cache_timeout == -1
    
    def test_cache_decorator_large_timeout(self):
        """Test cache decorator with very large timeout."""
        large_timeout = 86400 * 365  # 1 year in seconds
        
        @cache(timeout=large_timeout)
        def test_function():
            return {"data": "test"}
        
        assert hasattr(test_function, '_use_cache')
        assert test_function._use_cache is True
        assert hasattr(test_function, '_cache_timeout')
        assert test_function._cache_timeout == large_timeout
    
    def test_cache_decorator_preserves_function_attributes(self):
        """Test that cache decorator preserves original function attributes."""
        def original_function():
            """Original function docstring."""
            return {"data": "test"}
        
        original_function.custom_attr = "custom_value"
        
        decorated_function = cache(timeout=300)(original_function)
        
        # Check that original attributes are preserved
        assert decorated_function.__name__ == original_function.__name__
        assert decorated_function.__doc__ == original_function.__doc__
        assert hasattr(decorated_function, 'custom_attr')
        assert decorated_function.custom_attr == "custom_value"
        
        # Check that cache attributes are added
        assert hasattr(decorated_function, '_use_cache')
        assert hasattr(decorated_function, '_cache_timeout')
    
    def test_cache_decorator_with_async_function(self):
        """Test cache decorator works with async functions."""
        @cache(timeout=300)
        async def async_function():
            return {"data": "async_test"}
        
        assert hasattr(async_function, '_use_cache')
        assert async_function._use_cache is True
        assert hasattr(async_function, '_cache_timeout')
        assert async_function._cache_timeout == 300
    
    def test_cache_decorator_with_function_parameters(self):
        """Test cache decorator with function that has parameters."""
        @cache(timeout=300)
        def function_with_params(param1, param2="default"):
            return {"param1": param1, "param2": param2}
        
        assert hasattr(function_with_params, '_use_cache')
        assert function_with_params._use_cache is True
        assert hasattr(function_with_params, '_cache_timeout')
        assert function_with_params._cache_timeout == 300
        
        # Test that function still works
        result = function_with_params("test", "value")
        assert result == {"param1": "test", "param2": "value"}
    
    def test_cache_decorator_multiple_applications(self):
        """Test applying cache decorator multiple times."""
        @cache(timeout=600)
        @cache(timeout=300)
        def test_function():
            return {"data": "test"}
        
        # First decorator should win (innermost)
        assert hasattr(test_function, '_use_cache')
        assert test_function._use_cache is True
        assert hasattr(test_function, '_cache_timeout')
        assert test_function._cache_timeout == 600
    
    def test_cache_decorator_with_class_method(self):
        """Test cache decorator with class methods."""
        class TestClass:
            @cache(timeout=300)
            def method(self):
                return {"data": "method_test"}
            
            @staticmethod
            @cache(timeout=600)
            def static_method():
                return {"data": "static_test"}
            
            @classmethod
            @cache(timeout=900)
            def class_method(cls):
                return {"data": "class_test"}
        
        instance = TestClass()
        
        # Test instance method
        assert hasattr(instance.method, '_use_cache')
        assert instance.method._use_cache is True
        assert instance.method._cache_timeout == 300
        
        # Test static method (decorated function is accessible through class)
        assert hasattr(TestClass.static_method, '_use_cache')
        assert TestClass.static_method._use_cache is True
        assert TestClass.static_method._cache_timeout == 600
        
        # Test class method
        assert hasattr(TestClass.class_method, '_use_cache')
        assert TestClass.class_method._use_cache is True
        assert TestClass.class_method._cache_timeout == 900
    
    def test_cache_decorator_type_validation(self):
        """Test cache decorator with different timeout types."""
        # Test with float (should work)
        @cache(timeout=300.5)
        def test_function_float():
            return {"data": "test"}
        
        assert test_function_float._cache_timeout == 300.5
        
        # Test with string number (should work due to Python's flexibility)
        try:
            @cache(timeout="300")
            def test_function_string():
                return {"data": "test"}
            
            # If no exception, check the value
            assert test_function_string._cache_timeout == "300"
        except (TypeError, ValueError):
            # Expected behavior for strict type checking
            pass
    
    def test_cache_decorator_callable_check(self):
        """Test that cache decorator works only with callable objects."""
        # Test with regular function (should work)
        @cache(timeout=300)
        def regular_function():
            return "test"
        
        assert hasattr(regular_function, '_use_cache')
        
        # Test with lambda (should work)
        lambda_function = cache(timeout=300)(lambda: "test")
        assert hasattr(lambda_function, '_use_cache')
        
        # Test with callable class
        class CallableClass:
            def __call__(self):
                return "test"
        
        callable_instance = CallableClass()
        decorated_callable = cache(timeout=300)(callable_instance)
        assert hasattr(decorated_callable, '_use_cache')
