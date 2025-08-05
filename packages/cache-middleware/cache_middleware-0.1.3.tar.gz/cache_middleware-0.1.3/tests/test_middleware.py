"""
Tests for cache middleware.
"""
import pytest
import json
import asyncio
from unittest.mock import AsyncMock, Mock, patch, MagicMock, call
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from starlette.responses import Response
from cache_middleware.middleware import CacheMiddleware
from cache_middleware.decorators import cache
from conftest import MockRequest, MockRoute, MockApp


class TestCacheMiddleware:
    """Test cases for CacheMiddleware."""
    
    def test_cache_middleware_initialization(self, mock_cache_backend):
        """Test CacheMiddleware initialization."""
        app = FastAPI()
        
        middleware = CacheMiddleware(app, backend=mock_cache_backend)
        
        assert middleware.backend is mock_cache_backend
    
    @patch('cache_middleware.middleware.configure_logger')
    @patch('cache_middleware.middleware.logger')
    def test_cache_middleware_initialization_logging(self, mock_logger, mock_configure, mock_cache_backend):
        """Test that initialization logs correctly."""
        app = FastAPI()
        
        CacheMiddleware(app, backend=mock_cache_backend)
        
        mock_configure.assert_called_once()
        mock_logger.info.assert_called()
    
    @pytest.mark.asyncio
    async def test_dispatch_no_app_in_scope(self, mock_cache_backend):
        """Test dispatch when no app in request scope."""
        app = FastAPI()
        middleware = CacheMiddleware(app, backend=mock_cache_backend)
        
        request = MockRequest()
        request.scope = {"type": "http"}  # No "app" key
        
        call_next = AsyncMock(return_value=Response("test"))
        
        result = await middleware.dispatch(request, call_next)
        
        call_next.assert_called_once_with(request)
        assert result.body == b"test"
    
    @pytest.mark.asyncio
    async def test_dispatch_no_matching_route(self, mock_cache_backend):
        """Test dispatch when no matching route found."""
        app = FastAPI()
        middleware = CacheMiddleware(app, backend=mock_cache_backend)
        
        mock_app = MockApp()
        request = MockRequest()
        request.scope["app"] = mock_app
        
        call_next = AsyncMock(return_value=Response("test"))
        
        result = await middleware.dispatch(request, call_next)
        
        call_next.assert_called_once_with(request)
        assert result.body == b"test"
    
    @pytest.mark.asyncio
    async def test_dispatch_endpoint_without_cache_decorator(self, mock_cache_backend):
        """Test dispatch with endpoint that doesn't have cache decorator."""
        app = FastAPI()
        middleware = CacheMiddleware(app, backend=mock_cache_backend)
        
        # Create endpoint without cache decorator
        def endpoint():
            return {"message": "test"}
        
        mock_app = MockApp()
        route = mock_app.add_route(endpoint, methods=["GET"], path_regex=True)
        
        request = MockRequest(method="GET")
        request.scope["app"] = mock_app
        
        call_next = AsyncMock(return_value=Response("test"))
        
        result = await middleware.dispatch(request, call_next)
        
        call_next.assert_called_once_with(request)
        assert result.body == b"test"
    
    @pytest.mark.asyncio
    async def test_dispatch_cache_hit(self, mock_cache_backend):
        """Test dispatch with cache hit."""
        app = FastAPI()
        middleware = CacheMiddleware(app, backend=mock_cache_backend)
        
        # Create cached endpoint
        @cache(timeout=300)
        def endpoint():
            return {"message": "test"}
        
        mock_app = MockApp()
        mock_app.add_route(endpoint, methods=["GET"], path_regex=True)
        
        request = MockRequest(method="GET", url="http://test.com/api/test")
        request.scope["app"] = mock_app
        
        # Mock cache hit
        cached_response = {"message": "cached"}
        mock_cache_backend.get.return_value = json.dumps(cached_response)
        
        call_next = AsyncMock()
        
        result = await middleware.dispatch(request, call_next)
        
        # Should not call next middleware
        call_next.assert_not_called()
        
        # Should return cached response
        assert isinstance(result, JSONResponse)
        response_body = json.loads(result.body.decode())
        assert response_body == cached_response
    
    @pytest.mark.asyncio
    async def test_dispatch_cache_miss_json_response(self, mock_cache_backend):
        """Test dispatch with cache miss and JSON response."""
        app = FastAPI()
        middleware = CacheMiddleware(app, backend=mock_cache_backend)
        
        @cache(timeout=300)
        def endpoint():
            return {"message": "test"}
        
        mock_app = MockApp()
        mock_app.add_route(endpoint, methods=["GET"], path_regex=True)
        
        request = MockRequest(method="GET", url="http://test.com/api/test")
        request.scope["app"] = mock_app
        
        # Mock cache miss
        mock_cache_backend.get.return_value = None
        
        # Mock successful response
        response_data = {"message": "fresh"}
        call_next = AsyncMock(return_value=JSONResponse(response_data))
        
        result = await middleware.dispatch(request, call_next)
        
        call_next.assert_called_once_with(request)
        
        # Should cache the response
        mock_cache_backend.set.assert_called_once()
        
        # Should return the response
        assert isinstance(result, JSONResponse)
    
    @pytest.mark.asyncio
    async def test_dispatch_cache_miss_non_json_response(self, mock_cache_backend):
        """Test dispatch with cache miss and non-JSON response."""
        app = FastAPI()
        middleware = CacheMiddleware(app, backend=mock_cache_backend)
        
        @cache(timeout=300)
        def endpoint():
            return {"message": "test"}
        
        mock_app = MockApp()
        mock_app.add_route(endpoint, methods=["GET"], path_regex=True)
        
        request = MockRequest(method="GET")
        request.scope["app"] = mock_app
        
        # Mock cache miss
        mock_cache_backend.get.return_value = None
        
        # Mock non-JSON response
        call_next = AsyncMock(return_value=Response("plain text", media_type="text/plain"))
        
        result = await middleware.dispatch(request, call_next)
        
        call_next.assert_called_once_with(request)
        
        # Should not cache non-JSON response
        mock_cache_backend.set.assert_not_called()
        
        # Should return the response unchanged
        assert result.body == b"plain text"
    
    @pytest.mark.asyncio
    async def test_dispatch_cache_miss_error_response(self, mock_cache_backend):
        """Test dispatch with cache miss and error response."""
        app = FastAPI()
        middleware = CacheMiddleware(app, backend=mock_cache_backend)
        
        @cache(timeout=300)
        def endpoint():
            return {"message": "test"}
        
        mock_app = MockApp()
        mock_app.add_route(endpoint, methods=["GET"], path_regex=True)
        
        request = MockRequest(method="GET")
        request.scope["app"] = mock_app
        
        # Mock cache miss
        mock_cache_backend.get.return_value = None
        
        # Mock error response
        call_next = AsyncMock(return_value=JSONResponse({"error": "not found"}, status_code=404))
        
        result = await middleware.dispatch(request, call_next)
        
        call_next.assert_called_once_with(request)
        
        # Should not cache error response
        mock_cache_backend.set.assert_not_called()
        
        # Should return the error response
        assert result.status_code == 404
    
    @pytest.mark.asyncio
    async def test_dispatch_no_store_cache_control(self, mock_cache_backend):
        """Test dispatch with Cache-Control: no-store header."""
        app = FastAPI()
        middleware = CacheMiddleware(app, backend=mock_cache_backend)
        
        @cache(timeout=300)
        def endpoint():
            return {"message": "test"}
        
        mock_app = MockApp()
        mock_app.add_route(endpoint, methods=["GET"], path_regex=True)
        
        request = MockRequest(
            method="GET", 
            headers={"Cache-Control": "no-store"}
        )
        request.scope["app"] = mock_app
        
        call_next = AsyncMock(return_value=JSONResponse({"message": "fresh"}))
        
        result = await middleware.dispatch(request, call_next)
        
        call_next.assert_called_once_with(request)
        
        # Should not check cache or store response
        mock_cache_backend.get.assert_not_called()
        mock_cache_backend.set.assert_not_called()
    
    @pytest.mark.asyncio
    async def test_dispatch_no_cache_control(self, mock_cache_backend):
        """Test dispatch with Cache-Control: no-cache header."""
        app = FastAPI()
        middleware = CacheMiddleware(app, backend=mock_cache_backend)
        
        @cache(timeout=300)
        def endpoint():
            return {"message": "test"}
        
        mock_app = MockApp()
        mock_app.add_route(endpoint, methods=["GET"], path_regex=True)
        
        request = MockRequest(
            method="GET",
            headers={"Cache-Control": "no-cache"}
        )
        request.scope["app"] = mock_app
        
        mock_cache_backend.get.return_value = None
        call_next = AsyncMock(return_value=JSONResponse({"message": "fresh"}))
        
        result = await middleware.dispatch(request, call_next)
        
        call_next.assert_called_once_with(request)
        
        # Should skip cache retrieval but still cache the response
        mock_cache_backend.set.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_generate_cache_key_basic(self, mock_cache_backend):
        """Test cache key generation."""
        app = FastAPI()
        middleware = CacheMiddleware(app, backend=mock_cache_backend)
        
        request = MockRequest(method="GET", url="http://test.com/api/test")
        
        key = await middleware._generate_cache_key(request)
        
        assert key.startswith("cache:")
        assert len(key) > 10  # Should be a hashed key
    
    @pytest.mark.asyncio
    async def test_generate_cache_key_with_query_params(self, mock_cache_backend):
        """Test cache key generation with query parameters."""
        app = FastAPI()
        middleware = CacheMiddleware(app, backend=mock_cache_backend)
        
        request1 = MockRequest(method="GET", url="http://test.com/api/test?a=1&b=2")
        request2 = MockRequest(method="GET", url="http://test.com/api/test?b=2&a=1")
        
        key1 = await middleware._generate_cache_key(request1)
        key2 = await middleware._generate_cache_key(request2)
        
        # Should generate same key regardless of parameter order
        assert key1 == key2
    
    @pytest.mark.asyncio
    async def test_generate_cache_key_with_body(self, mock_cache_backend):
        """Test cache key generation with request body."""
        app = FastAPI()
        middleware = CacheMiddleware(app, backend=mock_cache_backend)
        
        request = MockRequest(
            method="POST", 
            url="http://test.com/api/test",
            body=b'{"data": "test"}'
        )
        
        key = await middleware._generate_cache_key(request)
        
        assert key.startswith("cache:")
        assert len(key) > 10
    
    @pytest.mark.asyncio
    async def test_generate_cache_key_different_methods(self, mock_cache_backend):
        """Test that different methods generate different cache keys."""
        app = FastAPI()
        middleware = CacheMiddleware(app, backend=mock_cache_backend)
        
        request_get = MockRequest(method="GET", url="http://test.com/api/test")
        request_post = MockRequest(method="POST", url="http://test.com/api/test")
        
        key_get = await middleware._generate_cache_key(request_get)
        key_post = await middleware._generate_cache_key(request_post)
        
        assert key_get != key_post
    
    @pytest.mark.asyncio
    async def test_generate_cache_key_different_paths(self, mock_cache_backend):
        """Test that different paths generate different cache keys."""
        app = FastAPI()
        middleware = CacheMiddleware(app, backend=mock_cache_backend)
        
        request1 = MockRequest(method="GET", url="http://test.com/api/test1")
        request2 = MockRequest(method="GET", url="http://test.com/api/test2")
        
        key1 = await middleware._generate_cache_key(request1)
        key2 = await middleware._generate_cache_key(request2)
        
        assert key1 != key2
    
    @pytest.mark.asyncio
    @patch('cache_middleware.middleware.logger')
    async def test_backend_error_handling_get(self, mock_logger, mock_cache_backend):
        """Test handling of backend errors during get operation."""
        app = FastAPI()
        middleware = CacheMiddleware(app, backend=mock_cache_backend)
        
        @cache(timeout=300)
        def endpoint():
            return {"message": "test"}
        
        mock_app = MockApp()
        mock_app.add_route(endpoint, methods=["GET"], path_regex=True)
        
        request = MockRequest(method="GET")
        request.scope["app"] = mock_app
        
        # Mock backend error
        mock_cache_backend.get.side_effect = Exception("Backend error")
        
        call_next = AsyncMock(return_value=JSONResponse({"message": "fresh"}))
        
        result = await middleware.dispatch(request, call_next)
        
        call_next.assert_called_once_with(request)
        mock_logger.error.assert_called()
    
    @pytest.mark.asyncio
    @patch('cache_middleware.middleware.logger')
    async def test_backend_error_handling_set(self, mock_logger, mock_cache_backend):
        """Test handling of backend errors during set operation."""
        app = FastAPI()
        middleware = CacheMiddleware(app, backend=mock_cache_backend)
        
        @cache(timeout=300)
        def endpoint():
            return {"message": "test"}
        
        mock_app = MockApp()
        mock_app.add_route(endpoint, methods=["GET"], path_regex=True)
        
        request = MockRequest(method="GET")
        request.scope["app"] = mock_app
        
        # Mock cache miss and set error
        mock_cache_backend.get.return_value = None
        mock_cache_backend.set.side_effect = Exception("Backend error")
        
        call_next = AsyncMock(return_value=JSONResponse({"message": "fresh"}))
        
        result = await middleware.dispatch(request, call_next)
        
        call_next.assert_called_once_with(request)
        mock_logger.error.assert_called()
    
    @pytest.mark.asyncio
    async def test_endpoint_with_different_timeout(self, mock_cache_backend):
        """Test endpoint with custom timeout value."""
        app = FastAPI()
        middleware = CacheMiddleware(app, backend=mock_cache_backend)
        
        @cache(timeout=600)  # Custom timeout
        def endpoint():
            return {"message": "test"}
        
        mock_app = MockApp()
        mock_app.add_route(endpoint, methods=["GET"], path_regex=True)
        
        request = MockRequest(method="GET")
        request.scope["app"] = mock_app
        
        mock_cache_backend.get.return_value = None
        call_next = AsyncMock(return_value=JSONResponse({"message": "fresh"}))
        
        await middleware.dispatch(request, call_next)
        
        # Should use custom timeout
        mock_cache_backend.set.assert_called_once()
        _, _, timeout = mock_cache_backend.set.call_args[0]
        assert timeout == 600
    
    @pytest.mark.asyncio
    async def test_json_response_caching(self, mock_cache_backend):
        """Test that only JSON responses are cached."""
        app = FastAPI()
        middleware = CacheMiddleware(app, backend=mock_cache_backend)
        
        @cache(timeout=300)
        def endpoint():
            return {"message": "test"}
        
        mock_app = MockApp()
        mock_app.add_route(endpoint, methods=["GET"], path_regex=True)
        
        request = MockRequest(method="GET")
        request.scope["app"] = mock_app
        
        mock_cache_backend.get.return_value = None
        
        response_data = {"message": "fresh", "status": "ok"}
        json_response = JSONResponse(response_data)
        call_next = AsyncMock(return_value=json_response)
        
        await middleware.dispatch(request, call_next)
        
        mock_cache_backend.set.assert_called_once()
        cached_value = mock_cache_backend.set.call_args[0][1]
        assert json.loads(cached_value) == response_data
    
    @pytest.mark.asyncio
    async def test_successful_status_code_only(self, mock_cache_backend):
        """Test that only successful responses (200) are cached."""
        app = FastAPI()
        middleware = CacheMiddleware(app, backend=mock_cache_backend)
        
        @cache(timeout=300)
        def endpoint():
            return {"message": "test"}
        
        mock_app = MockApp()
        mock_app.add_route(endpoint, methods=["GET"], path_regex=True)
        
        request = MockRequest(method="GET")
        request.scope["app"] = mock_app
        
        mock_cache_backend.get.return_value = None
        
        status_codes = [200, 201, 400, 404, 500]
        
        for status_code in status_codes:
            mock_cache_backend.set.reset_mock()
            
            response = JSONResponse({"status": status_code}, status_code=status_code)
            call_next = AsyncMock(return_value=response)
            
            await middleware.dispatch(request, call_next)
            
            if status_code == 200:
                mock_cache_backend.set.assert_called_once()
            else:
                mock_cache_backend.set.assert_not_called()
    
    @pytest.mark.asyncio
    async def test_concurrent_cache_operations(self, mock_cache_backend):
        """Test concurrent cache operations."""
        app = FastAPI()
        middleware = CacheMiddleware(app, backend=mock_cache_backend)
        
        @cache(timeout=300)
        def endpoint():
            return {"message": "test"}
        
        mock_app = MockApp()
        mock_app.add_route(endpoint, methods=["GET"], path_regex=True)
        
        mock_cache_backend.get.return_value = None
        
        async def make_request(i):
            request = MockRequest(method="GET", url=f"http://test.com/api/test?id={i}")
            request.scope["app"] = mock_app
            
            call_next = AsyncMock(return_value=JSONResponse({"id": i}))
            return await middleware.dispatch(request, call_next)
        
        # Make concurrent requests
        tasks = [make_request(i) for i in range(5)]
        results = await asyncio.gather(*tasks)
        
        assert len(results) == 5
        # Each request should have been processed
        assert mock_cache_backend.set.call_count == 5


class TestCacheMiddlewareEdgeCases:
    """Test edge cases and error scenarios for CacheMiddleware."""
    
    @pytest.mark.asyncio
    async def test_malformed_cached_json(self, mock_cache_backend):
        """Test handling of malformed JSON in cache."""
        app = FastAPI()
        middleware = CacheMiddleware(app, backend=mock_cache_backend)
        
        @cache(timeout=300)
        def endpoint():
            return {"message": "test"}
        
        mock_app = MockApp()
        mock_app.add_route(endpoint, methods=["GET"], path_regex=True)
        
        request = MockRequest(method="GET")
        request.scope["app"] = mock_app
        
        # Mock cache returning malformed JSON
        mock_cache_backend.get.return_value = "invalid json {"
        
        call_next = AsyncMock(return_value=JSONResponse({"message": "fresh"}))
        
        with patch('cache_middleware.middleware.logger') as mock_logger:
            result = await middleware.dispatch(request, call_next)
            
            # Should call next middleware due to JSON error
            call_next.assert_called_once_with(request)
            mock_logger.error.assert_called()
    
    @pytest.mark.asyncio
    async def test_empty_request_body(self, mock_cache_backend):
        """Test handling of empty request body."""
        app = FastAPI()
        middleware = CacheMiddleware(app, backend=mock_cache_backend)
        
        request = MockRequest(method="POST", body=b"")
        
        key = await middleware._generate_cache_key(request)
        
        assert key is not None
        assert key.startswith("cache:")
    
    @pytest.mark.asyncio
    async def test_very_large_request_body(self, mock_cache_backend):
        """Test handling of very large request body."""
        app = FastAPI()
        middleware = CacheMiddleware(app, backend=mock_cache_backend)
        
        large_body = b"x" * 100000  # 100KB body
        request = MockRequest(method="POST", body=large_body)
        
        key = await middleware._generate_cache_key(request)
        
        assert key is not None
        assert key.startswith("cache:")
    
    @pytest.mark.asyncio
    async def test_unicode_in_request_data(self, mock_cache_backend):
        """Test handling of Unicode data in requests."""
        app = FastAPI()
        middleware = CacheMiddleware(app, backend=mock_cache_backend)
        
        unicode_body = '{"message": "Hello 世界 🌍"}'.encode('utf-8')
        request = MockRequest(
            method="POST", 
            url="http://test.com/api/测试",
            body=unicode_body
        )
        
        key = await middleware._generate_cache_key(request)
        
        assert key is not None
        assert key.startswith("cache:")
    
    @pytest.mark.asyncio
    async def test_multiple_cache_control_directives(self, mock_cache_backend):
        """Test handling of multiple Cache-Control directives."""
        app = FastAPI()
        middleware = CacheMiddleware(app, backend=mock_cache_backend)
        
        @cache(timeout=300)
        def endpoint():
            return {"message": "test"}
        
        mock_app = MockApp()
        mock_app.add_route(endpoint, methods=["GET"], path_regex=True)
        
        request = MockRequest(
            method="GET",
            headers={"Cache-Control": "no-cache, max-age=0, must-revalidate"}
        )
        request.scope["app"] = mock_app
        
        mock_cache_backend.get.return_value = None
        call_next = AsyncMock(return_value=JSONResponse({"message": "fresh"}))
        
        result = await middleware.dispatch(request, call_next)
        
        # Should handle no-cache directive
        call_next.assert_called_once_with(request)
    
    @pytest.mark.asyncio
    async def test_route_without_path_regex(self, mock_cache_backend):
        """Test route without path_regex attribute."""
        app = FastAPI()
        middleware = CacheMiddleware(app, backend=mock_cache_backend)
        
        mock_app = MockApp()
        # Create route without path_regex
        route = MockRoute(endpoint=lambda: {"test": "data"}, methods=["GET"])
        route.path_regex = None
        mock_app.routes.append(route)
        
        request = MockRequest(method="GET")
        request.scope["app"] = mock_app
        
        call_next = AsyncMock(return_value=Response("test"))
        
        result = await middleware.dispatch(request, call_next)
        
        # Should call next middleware
        call_next.assert_called_once_with(request)
    
    @pytest.mark.asyncio
    async def test_route_without_methods(self, mock_cache_backend):
        """Test route without methods attribute."""
        app = FastAPI()
        middleware = CacheMiddleware(app, backend=mock_cache_backend)
        
        mock_app = MockApp()
        # Create route without methods
        route = MockRoute(endpoint=lambda: {"test": "data"}, path_regex=True)
        route.methods = None
        mock_app.routes.append(route)
        
        request = MockRequest(method="GET")
        request.scope["app"] = mock_app
        
        call_next = AsyncMock(return_value=Response("test"))
        
        result = await middleware.dispatch(request, call_next)
        
        # Should call next middleware
        call_next.assert_called_once_with(request)
