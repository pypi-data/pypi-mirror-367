"""
FastAPI/Starlette caching middleware implementation.

This module provides HTTP response caching capabilities through a middleware
that integrates with configurable cache backends.
"""
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware
from urllib.parse import urlencode
import hashlib
import json

from cache_middleware.logger_config import logger, configure_logger
from cache_middleware.backends import CacheBackend


class CacheMiddleware(BaseHTTPMiddleware):
    """
    HTTP caching middleware for FastAPI/Starlette applications.
    
    This middleware intercepts HTTP requests and provides response caching
    using a configurable backend. It works in conjunction with the @cache
    decorator to determine which endpoints should be cached.
    
    Parameters
    ----------
    app : FastAPI
        The FastAPI application instance
    backend : CacheBackend
        A fully initialized cache backend instance that implements
        the CacheBackend interface
        
    Examples
    --------
    >>> from cache_middleware.backends.redis_backend import RedisBackend
    >>> redis_backend = RedisBackend(url="redis://localhost:6379")
    >>> app.add_middleware(CacheMiddleware, backend=redis_backend)
    """
    
    def __init__(self, app: FastAPI, backend: CacheBackend):
        """
        Initialize the cache middleware.
        
        Parameters
        ----------
        app : FastAPI
            The FastAPI application instance
        backend : CacheBackend
            A fully initialized cache backend instance
        """
        super().__init__(app)
        configure_logger()
        
        self.backend = backend
        logger.info(f"Cache middleware initialized with {type(backend).__name__} backend")

    async def _generate_cache_key(self, request: Request) -> str:
        """
        Generate a unique cache key based on request details.
        
        Parameters
        ----------
        request : Request
            The incoming HTTP request
            
        Returns
        -------
        str
            A unique cache key for this request
        """
        query_params = dict(request.query_params)
        sorted_params = urlencode(sorted(query_params.items()))
        body_bytes = await request.body()
        key_base = f"{request.method}:{request.url.path}?{sorted_params}|{body_bytes.decode()}"
        cache_key = f"cache:{hashlib.sha256(key_base.encode()).hexdigest()}"
        return cache_key

    async def dispatch(self, request: Request, call_next):
        """
        Process HTTP requests and apply caching logic.
        
        This method intercepts incoming requests, checks if the endpoint
        has caching enabled via the @cache decorator, and either returns
        a cached response or caches the response from the endpoint.
        
        Parameters
        ----------
        request : Request
            The incoming HTTP request
        call_next : callable
            The next middleware or endpoint in the chain
            
        Returns
        -------
        Response
            Either a cached JSONResponse or the response from the endpoint
            
        Notes
        -----
        The caching logic follows these steps:
        1. Find the endpoint function from the application routes
        2. Check if endpoint has the _use_cache attribute (set by @cache decorator)
        3. Handle Cache-Control headers (no-store, no-cache)
        4. Generate a unique cache key based on method, path, params, and body
        5. Try to return cached response if available
        6. Call the actual endpoint and cache successful JSON responses
        """
        # Find the route that matches the path and method
        app = request.scope.get("app")
        if not app:
            return await call_next(request)

        # Search for the endpoint in the application routes
        endpoint = None
        path = request.scope.get("path", "")
        method = request.scope.get("method", "")
        
        # Iterate through FastAPI routes to find matching endpoint
        for route in app.routes:
            if hasattr(route, 'path_regex') and hasattr(route, 'methods'):
                # Check if methods and path_regex are not None and match
                if (route.methods is not None and method in route.methods and
                    route.path_regex is not None and route.path_regex.match(path)):
                    endpoint = getattr(route, 'endpoint', None)
                    break
        
        if not endpoint:
            return await call_next(request)

        # Check if the endpoint has caching enabled
        if not getattr(endpoint, "_use_cache", False):
            return await call_next(request)

        # Handle Cache-Control headers
        cache_control = request.headers.get("cache-control", "") or request.headers.get("Cache-Control", "")
        cache_control = cache_control.lower()
        if "no-store" in cache_control:
            return await call_next(request)

        # Generate unique cache key
        cache_key = await self._generate_cache_key(request)

        timeout = getattr(endpoint, "_cache_timeout", 60)

        # Try to return from cache (if no no-cache directive)
        if "no-cache" not in cache_control:
            try:
                cached_data = await self.backend.get(cache_key)
                if cached_data:
                    try:
                        logger.debug(f"Cache hit for key: {cache_key}")
                        data = json.loads(cached_data)
                        return JSONResponse(content=data)
                    except json.JSONDecodeError:
                        logger.error(f"Malformed JSON in cache for key: {cache_key}, ignoring cached data")
                        # Continue to call the actual endpoint
            except Exception as e:
                logger.error(f"Backend error during get operation: {e}")
                # Continue to call the actual endpoint

        # Call the actual endpoint
        response = await call_next(request)

        # Cache only successful JSON responses
        if response.status_code == 200 and "application/json" in response.headers.get("content-type", ""):
            # For JSONResponse, get the content directly
            if hasattr(response, 'body'):
                response_body = response.body.decode()
            elif hasattr(response, 'content'):
                # JSONResponse stores content as dict/object, serialize it
                response_body = json.dumps(response.content)
            else:
                # Fallback: try to read from body_iterator if available
                try:
                    body = [chunk async for chunk in response.body_iterator]
                    response_body = b"".join(body).decode()
                    # Recreate response to avoid losing body content
                    response = JSONResponse(content=json.loads(response_body), status_code=response.status_code)
                except AttributeError:
                    # Skip caching if we can't read the body
                    return response

            # Store in backend
            try:
                await self.backend.set(cache_key, response_body, timeout)
            except Exception as e:
                logger.error(f"Backend error during set operation: {e}")
                # Continue anyway, don't fail the response

        return response
