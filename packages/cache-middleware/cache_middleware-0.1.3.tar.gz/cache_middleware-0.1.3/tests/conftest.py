"""
Pytest configuration and shared fixtures.
"""
import pytest
import asyncio
from unittest.mock import AsyncMock, Mock, patch, MagicMock
from fastapi import FastAPI
from fastapi.testclient import TestClient
from cache_middleware.backends import CacheBackend


class MockRoute:
    """Mock route for testing."""
    
    def __init__(self, endpoint, methods=None, path_regex=None):
        self.endpoint = endpoint
        self.methods = methods or ["GET"]
        if path_regex is True:
            # Create a mock regex object that always matches
            self.path_regex = MagicMock()
            self.path_regex.match.return_value = True
        else:
            self.path_regex = path_regex


@pytest.fixture(scope="session")
def event_loop():
    """Create an instance of the default event loop for the test session."""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


@pytest.fixture
def mock_cache_backend():
    """Create a mock cache backend for testing."""
    backend = AsyncMock(spec=CacheBackend)
    backend.get.return_value = None
    backend.set.return_value = None
    backend.delete.return_value = None
    backend.close.return_value = None
    return backend


@pytest.fixture
def sample_app():
    """Create a sample FastAPI app for testing."""
    app = FastAPI()
    
    @app.get("/")
    async def root():
        return {"message": "Hello World"}
    
    @app.get("/items/{item_id}")
    async def get_item(item_id: int):
        return {"item_id": item_id, "name": f"Item {item_id}"}
    
    @app.post("/calculate")
    async def calculate(data: dict):
        numbers = data.get("numbers", [])
        return {"result": sum(numbers), "count": len(numbers)}
    
    return app


@pytest.fixture
def test_client(sample_app):
    """Create a test client for the sample app."""
    return TestClient(sample_app)


@pytest.fixture
def mock_redis():
    """Mock Redis connection for testing."""
    with patch('cache_middleware.backends.redis_backend.aioredis') as mock:
        redis_instance = AsyncMock()
        mock.from_url.return_value = redis_instance
        yield redis_instance


@pytest.fixture
def mock_memcached():
    """Mock Memcached connection for testing."""
    with patch('cache_middleware.backends.memcached_backend.aiomcache.Client') as mock:
        memcached_instance = AsyncMock()
        mock.return_value = memcached_instance
        yield memcached_instance


@pytest.fixture
def mock_logger():
    """Mock logger for testing."""
    with patch('cache_middleware.logger_config.logger') as mock:
        yield mock


class MockRequest:
    """Mock request object for testing."""
    
    def __init__(self, method="GET", url="http://test.com/", body=b"", headers=None):
        self.method = method
        self.url = MockURL(url)
        self._body = body
        self.headers = headers or {}
        self.scope = {
            "type": "http",
            "method": method,
            "path": self.url.path,
            "query_string": self.url.query.encode() if self.url.query else b"",
            "headers": [(k.encode(), v.encode()) for k, v in self.headers.items()],
            "app": MockApp()
        }
    
    @property
    def query_params(self):
        """Return query parameters as a dict-like object."""
        from urllib.parse import parse_qs
        parsed = parse_qs(self.url.query)
        # Flatten single-item lists to match FastAPI's behavior
        return {k: v[0] if len(v) == 1 else v for k, v in parsed.items()}
    
    async def body(self):
        return self._body


class MockURL:
    """Mock URL object for testing."""
    
    def __init__(self, url):
        from urllib.parse import urlparse, parse_qs
        parsed = urlparse(url)
        self.scheme = parsed.scheme
        self.netloc = parsed.netloc
        self.path = parsed.path
        self.query = parsed.query
        self.fragment = parsed.fragment
        self.params = parse_qs(parsed.query)


class MockApp:
    """Mock FastAPI app for testing."""
    
    def __init__(self):
        self.routes = []
    
    def add_route(self, endpoint, methods=None, path_regex=None):
        route = MockRoute(endpoint=endpoint, methods=methods, path_regex=path_regex)
        self.routes.append(route)
        return route


@pytest.fixture
def mock_request():
    """Create a mock request for testing."""
    return MockRequest()


@pytest.fixture
def mock_response():
    """Create a mock response for testing."""
    response = Mock()
    response.status_code = 200
    response.headers = {"content-type": "application/json"}
    response.body = b'{"message": "test"}'
    return response
