"""
Cache decorators for FastAPI/Starlette endpoints.

This module provides decorators to mark endpoints for caching.
The actual caching logic is implemented in the CacheMiddleware.
"""


def cache(timeout: int = 300):
    """
    Decorator to enable caching for a FastAPI endpoint.
    
    This decorator marks a function as cacheable by setting internal
    attributes that the CacheMiddleware will inspect. The decorator
    itself doesn't perform any caching - it only provides metadata
    to the middleware.
    
    Parameters
    ----------
    timeout : int, default=300
        Cache expiration timeout in seconds
        
    Returns
    -------
    callable
        The decorator function that marks the endpoint for caching
        
    Examples
    --------
    >>> @app.get("/items")
    >>> @cache(timeout=600)  # Cache for 10 minutes
    >>> async def get_items():
    ...     return {"items": [1, 2, 3]}
    
    >>> @app.post("/calculate")
    >>> @cache(timeout=120)  # Cache for 2 minutes
    >>> async def calculate(data: dict):
    ...     return {"result": sum(data.get("numbers", []))}
        
    Notes
    -----
    The decorator sets two attributes on the function:
    - _use_cache: Boolean flag indicating caching is enabled
    - _cache_timeout: Integer timeout value in seconds
    
    The CacheMiddleware looks for these attributes to determine
    which endpoints should be cached and for how long.
    """
    def decorator(func):
        """
        Inner decorator that sets caching attributes on the function.
        
        Parameters
        ----------
        func : callable
            The FastAPI endpoint function to be cached
            
        Returns
        -------
        callable
            The original function with caching attributes set
        """
        setattr(func, "_use_cache", True)
        setattr(func, "_cache_timeout", timeout)
        return func
    return decorator


