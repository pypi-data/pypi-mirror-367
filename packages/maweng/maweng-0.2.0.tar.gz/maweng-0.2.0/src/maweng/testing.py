"""
Testing utilities for the Maweng framework.

This module provides testing utilities including test clients, fixtures,
and assertions for testing Maweng applications.
"""

import asyncio
import json
from typing import Any, Dict, List, Optional, Union
from contextlib import asynccontextmanager

import pytest
from fastapi.testclient import TestClient as FastAPITestClient
from httpx import AsyncClient

from .app import App
from .config import TestingConfig


class TestClient:
    """
    Test client for Maweng applications.
    
    This class provides a convenient interface for testing Maweng applications
    with both synchronous and asynchronous request methods.
    """
    
    def __init__(self, app: Union[App, Any]) -> None:
        """
        Initialize the test client.
        
        Args:
            app: Maweng app or FastAPI app instance
        """
        if isinstance(app, App):
            self.app = app.fastapi_app
        else:
            self.app = app
        
        self.client = FastAPITestClient(self.app)
        self.async_client: Optional[AsyncClient] = None
    
    def __enter__(self):
        """Enter context manager."""
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Exit context manager."""
        self.close()
    
    def close(self) -> None:
        """Close the test client."""
        if self.async_client:
            asyncio.run(self.async_client.aclose())
    
    # Synchronous methods
    def get(self, url: str, **kwargs: Any) -> 'TestResponse':
        """Make a GET request."""
        response = self.client.get(url, **kwargs)
        return TestResponse(response)
    
    def post(self, url: str, **kwargs: Any) -> 'TestResponse':
        """Make a POST request."""
        response = self.client.post(url, **kwargs)
        return TestResponse(response)
    
    def put(self, url: str, **kwargs: Any) -> 'TestResponse':
        """Make a PUT request."""
        response = self.client.put(url, **kwargs)
        return TestResponse(response)
    
    def delete(self, url: str, **kwargs: Any) -> 'TestResponse':
        """Make a DELETE request."""
        response = self.client.delete(url, **kwargs)
        return TestResponse(response)
    
    def patch(self, url: str, **kwargs: Any) -> 'TestResponse':
        """Make a PATCH request."""
        response = self.client.patch(url, **kwargs)
        return TestResponse(response)
    
    def options(self, url: str, **kwargs: Any) -> 'TestResponse':
        """Make an OPTIONS request."""
        response = self.client.options(url, **kwargs)
        return TestResponse(response)
    
    def head(self, url: str, **kwargs: Any) -> 'TestResponse':
        """Make a HEAD request."""
        response = self.client.head(url, **kwargs)
        return TestResponse(response)
    
    # Asynchronous methods
    async def aget(self, url: str, **kwargs: Any) -> 'TestResponse':
        """Make an async GET request."""
        if not self.async_client:
            self.async_client = AsyncClient(app=self.app, base_url="http://test")
        
        response = await self.async_client.get(url, **kwargs)
        return TestResponse(response)
    
    async def apost(self, url: str, **kwargs: Any) -> 'TestResponse':
        """Make an async POST request."""
        if not self.async_client:
            self.async_client = AsyncClient(app=self.app, base_url="http://test")
        
        response = await self.async_client.post(url, **kwargs)
        return TestResponse(response)
    
    async def aput(self, url: str, **kwargs: Any) -> 'TestResponse':
        """Make an async PUT request."""
        if not self.async_client:
            self.async_client = AsyncClient(app=self.app, base_url="http://test")
        
        response = await self.async_client.put(url, **kwargs)
        return TestResponse(response)
    
    async def adelete(self, url: str, **kwargs: Any) -> 'TestResponse':
        """Make an async DELETE request."""
        if not self.async_client:
            self.async_client = AsyncClient(app=self.app, base_url="http://test")
        
        response = await self.async_client.delete(url, **kwargs)
        return TestResponse(response)
    
    async def apatch(self, url: str, **kwargs: Any) -> 'TestResponse':
        """Make an async PATCH request."""
        if not self.async_client:
            self.async_client = AsyncClient(app=self.app, base_url="http://test")
        
        response = await self.async_client.patch(url, **kwargs)
        return TestResponse(response)
    
    # Utility methods
    def set_auth_token(self, token: str) -> None:
        """Set authentication token for subsequent requests."""
        self.client.headers.update({"Authorization": f"Bearer {token}"})
    
    def clear_auth_token(self) -> None:
        """Clear authentication token."""
        if "Authorization" in self.client.headers:
            del self.client.headers["Authorization"]
    
    def set_cookie(self, name: str, value: str) -> None:
        """Set a cookie for subsequent requests."""
        self.client.cookies.set(name, value)
    
    def clear_cookies(self) -> None:
        """Clear all cookies."""
        self.client.cookies.clear()


class TestResponse:
    """Wrapper for test response with additional assertions."""
    
    def __init__(self, response: Any) -> None:
        """
        Initialize the test response.
        
        Args:
            response: HTTPX or FastAPI test response
        """
        self.response = response
        self.status_code = response.status_code
        self.headers = dict(response.headers)
        self.cookies = dict(response.cookies)
        
        # Parse JSON content if possible
        try:
            self.json = response.json()
        except (json.JSONDecodeError, AttributeError):
            self.json = None
        
        self.text = getattr(response, 'text', str(response.content))
    
    def assert_status(self, status_code: int) -> 'TestResponse':
        """Assert response status code."""
        assert self.status_code == status_code, f"Expected status {status_code}, got {self.status_code}"
        return self
    
    def assert_ok(self) -> 'TestResponse':
        """Assert response is successful (2xx)."""
        assert 200 <= self.status_code < 300, f"Expected 2xx status, got {self.status_code}"
        return self
    
    def assert_created(self) -> 'TestResponse':
        """Assert response is 201 Created."""
        return self.assert_status(201)
    
    def assert_no_content(self) -> 'TestResponse':
        """Assert response is 204 No Content."""
        return self.assert_status(204)
    
    def assert_bad_request(self) -> 'TestResponse':
        """Assert response is 400 Bad Request."""
        return self.assert_status(400)
    
    def assert_unauthorized(self) -> 'TestResponse':
        """Assert response is 401 Unauthorized."""
        return self.assert_status(401)
    
    def assert_forbidden(self) -> 'TestResponse':
        """Assert response is 403 Forbidden."""
        return self.assert_status(403)
    
    def assert_not_found(self) -> 'TestResponse':
        """Assert response is 404 Not Found."""
        return self.assert_status(404)
    
    def assert_internal_server_error(self) -> 'TestResponse':
        """Assert response is 500 Internal Server Error."""
        return self.assert_status(500)
    
    def assert_json(self) -> 'TestResponse':
        """Assert response has JSON content."""
        assert self.json is not None, "Response is not JSON"
        return self
    
    def assert_json_contains(self, key: str, value: Any = None) -> 'TestResponse':
        """Assert JSON response contains key (and optionally value)."""
        self.assert_json()
        assert key in self.json, f"Key '{key}' not found in response"
        if value is not None:
            assert self.json[key] == value, f"Expected {value}, got {self.json[key]}"
        return self
    
    def assert_json_equals(self, expected: Dict[str, Any]) -> 'TestResponse':
        """Assert JSON response equals expected data."""
        self.assert_json()
        assert self.json == expected, f"Expected {expected}, got {self.json}"
        return self
    
    def assert_has_header(self, header: str, value: str = None) -> 'TestResponse':
        """Assert response has header (and optionally value)."""
        header_lower = header.lower()
        assert header_lower in self.headers, f"Header '{header}' not found"
        if value is not None:
            assert self.headers[header_lower] == value, f"Expected {value}, got {self.headers[header_lower]}"
        return self
    
    def assert_has_cookie(self, name: str, value: str = None) -> 'TestResponse':
        """Assert response has cookie (and optionally value)."""
        assert name in self.cookies, f"Cookie '{name}' not found"
        if value is not None:
            assert self.cookies[name] == value, f"Expected {value}, got {self.cookies[name]}"
        return self
    
    def assert_redirects_to(self, url: str) -> 'TestResponse':
        """Assert response redirects to URL."""
        assert 300 <= self.status_code < 400, f"Expected redirect status, got {self.status_code}"
        location = self.headers.get('location', '')
        assert location == url, f"Expected redirect to {url}, got {location}"
        return self


# Test fixtures
@pytest.fixture
def test_app() -> App:
    """Create a test application."""
    config = TestingConfig()
    return App("test-app", config=config)


@pytest.fixture
def test_client(test_app: App) -> TestClient:
    """Create a test client."""
    return TestClient(test_app)


@pytest.fixture
async def async_test_client(test_app: App) -> TestClient:
    """Create an async test client."""
    client = TestClient(test_app)
    yield client
    client.close()


@pytest.fixture
def test_database():
    """Create a test database."""
    # This would set up a test database
    # For now, just yield None
    yield None


# Test utilities
def create_test_user(client: TestClient, user_data: Dict[str, Any] = None) -> Dict[str, Any]:
    """
    Create a test user.
    
    Args:
        client: Test client
        user_data: User data
        
    Returns:
        Created user data
    """
    if user_data is None:
        user_data = {
            "email": "test@example.com",
            "password": "testpassword",
            "name": "Test User"
        }
    
    response = client.post("/users", json=user_data)
    response.assert_created()
    return response.json


def login_test_user(client: TestClient, email: str = "test@example.com", password: str = "testpassword") -> str:
    """
    Login a test user and return token.
    
    Args:
        client: Test client
        email: User email
        password: User password
        
    Returns:
        Authentication token
    """
    response = client.post("/auth/login", json={"email": email, "password": password})
    response.assert_ok()
    return response.json["token"]


def create_authenticated_client(client: TestClient, email: str = "test@example.com", password: str = "testpassword") -> TestClient:
    """
    Create an authenticated test client.
    
    Args:
        client: Test client
        email: User email
        password: User password
        
    Returns:
        Authenticated test client
    """
    token = login_test_user(client, email, password)
    client.set_auth_token(token)
    return client


# Test decorators
def requires_auth(func):
    """Decorator to require authentication for tests."""
    def wrapper(*args, **kwargs):
        # This would check if the test requires authentication
        # and set up the necessary auth context
        return func(*args, **kwargs)
    return wrapper


def skip_if_no_database(func):
    """Decorator to skip tests if no database is available."""
    def wrapper(*args, **kwargs):
        # This would check if a database is available
        # and skip the test if not
        return func(*args, **kwargs)
    return wrapper


# Test assertions
def assert_model_created(model_class, **filters):
    """Assert that a model was created with the given filters."""
    # This would check if a model exists in the database
    pass


def assert_model_updated(model_class, id: Any, **updates):
    """Assert that a model was updated with the given values."""
    # This would check if a model was updated in the database
    pass


def assert_model_deleted(model_class, id: Any):
    """Assert that a model was deleted."""
    # This would check if a model was deleted from the database
    pass


# Test data generators
def generate_user_data(**overrides: Any) -> Dict[str, Any]:
    """Generate test user data."""
    import random
    import string
    
    base_data = {
        "email": f"test{random.randint(1000, 9999)}@example.com",
        "password": "".join(random.choices(string.ascii_letters + string.digits, k=12)),
        "name": f"Test User {random.randint(1000, 9999)}"
    }
    
    base_data.update(overrides)
    return base_data


def generate_post_data(**overrides: Any) -> Dict[str, Any]:
    """Generate test post data."""
    import random
    
    base_data = {
        "title": f"Test Post {random.randint(1000, 9999)}",
        "content": f"This is test content {random.randint(1000, 9999)}",
        "published": True
    }
    
    base_data.update(overrides)
    return base_data


# Test helpers
@asynccontextmanager
async def test_database_session():
    """Context manager for test database sessions."""
    # This would provide a test database session
    # For now, just yield None
    yield None


def cleanup_test_data():
    """Clean up test data after tests."""
    # This would clean up any test data created during tests
    pass 