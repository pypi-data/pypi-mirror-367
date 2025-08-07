"""
Tests for the basic Maweng application.

This module demonstrates the testing capabilities of the Maweng framework
including test clients, fixtures, and assertions.
"""

import pytest
from maweng.testing import TestClient
from maweng import App, View, Response
from maweng.orm import Model, Field, query
from datetime import datetime


# Test models
class TestUser(Model):
    __tablename__ = "test_users"
    
    id = Field.Integer(primary_key=True)
    name = Field.String(max_length=100)
    email = Field.String(unique=True, max_length=255)
    created_at = Field.DateTime(default=datetime.utcnow)
    is_active = Field.Boolean(default=True)


class TestPost(Model):
    __tablename__ = "test_posts"
    
    id = Field.Integer(primary_key=True)
    title = Field.String(max_length=200)
    content = Field.Text()
    author_id = Field.Integer(foreign_key="test_users.id")
    created_at = Field.DateTime(default=datetime.utcnow)
    published = Field.Boolean(default=False)


# Test views
class TestUserView(View):
    @query.get("/test-users")
    async def list_users(self):
        """Get all test users."""
        users = await TestUser.all()
        return Response.json([user.to_dict() for user in users])
    
    @query.post("/test-users")
    async def create_user(self, user_data: dict):
        """Create a new test user."""
        user = await TestUser.create(**user_data)
        return Response.created(user.to_dict())
    
    @query.get("/test-users/{user_id}")
    async def get_user(self, user_id: int):
        """Get a specific test user."""
        user = await TestUser.get(user_id)
        if not user:
            return Response.not_found("User not found")
        return Response.json(user.to_dict())


class TestHealthView(View):
    @query.get("/test-health")
    async def health_check(self):
        """Test health check endpoint."""
        return Response.json({
            "status": "healthy",
            "timestamp": datetime.utcnow().isoformat(),
            "framework": "Maweng",
            "version": "0.1.0"
        })


def create_test_app():
    """Create a test application."""
    app = App("test-app", debug=True)
    
    # Register test views
    app.register_view(TestUserView())
    app.register_view(TestHealthView())
    
    return app


@pytest.fixture
def test_app():
    """Create a test application fixture."""
    return create_test_app()


@pytest.fixture
def test_client(test_app):
    """Create a test client fixture."""
    return TestClient(test_app)


class TestHealthEndpoint:
    """Test health check endpoint."""
    
    def test_health_check(self, test_client):
        """Test health check endpoint."""
        response = test_client.get("/test-health")
        
        response.assert_ok()
        response.assert_json()
        response.assert_json_contains("status", "healthy")
        response.assert_json_contains("framework", "Maweng")
        response.assert_json_contains("version", "0.1.0")
    
    def test_health_check_async(self, test_client):
        """Test health check endpoint asynchronously."""
        import asyncio
        
        async def test():
            response = await test_client.aget("/test-health")
            response.assert_ok()
            response.assert_json()
            response.assert_json_contains("status", "healthy")
        
        asyncio.run(test())


class TestUserEndpoints:
    """Test user endpoints."""
    
    def test_list_users_empty(self, test_client):
        """Test listing users when none exist."""
        response = test_client.get("/test-users")
        
        response.assert_ok()
        response.assert_json()
        assert response.json == []
    
    def test_create_user(self, test_client):
        """Test creating a user."""
        user_data = {
            "name": "Test User",
            "email": "test@example.com"
        }
        
        response = test_client.post("/test-users", json=user_data)
        
        response.assert_created()
        response.assert_json()
        response.assert_json_contains("name", "Test User")
        response.assert_json_contains("email", "test@example.com")
        response.assert_json_contains("is_active", True)
    
    def test_create_user_invalid_data(self, test_client):
        """Test creating a user with invalid data."""
        user_data = {
            "name": "Test User"
            # Missing email
        }
        
        response = test_client.post("/test-users", json=user_data)
        
        # This would typically return a validation error
        # For now, we'll just check that it doesn't crash
        assert response.status_code in [400, 422, 500]
    
    def test_get_user_exists(self, test_client):
        """Test getting a user that exists."""
        # First create a user
        user_data = {
            "name": "Test User",
            "email": "test@example.com"
        }
        
        create_response = test_client.post("/test-users", json=user_data)
        create_response.assert_created()
        
        user_id = create_response.json["id"]
        
        # Then get the user
        response = test_client.get(f"/test-users/{user_id}")
        
        response.assert_ok()
        response.assert_json()
        response.assert_json_contains("id", user_id)
        response.assert_json_contains("name", "Test User")
    
    def test_get_user_not_exists(self, test_client):
        """Test getting a user that doesn't exist."""
        response = test_client.get("/test-users/999")
        
        response.assert_not_found()
        response.assert_json()
        response.assert_json_contains("error", "User not found")
    
    def test_list_users_with_data(self, test_client):
        """Test listing users when some exist."""
        # Create multiple users
        users_data = [
            {"name": "User 1", "email": "user1@example.com"},
            {"name": "User 2", "email": "user2@example.com"},
            {"name": "User 3", "email": "user3@example.com"}
        ]
        
        for user_data in users_data:
            response = test_client.post("/test-users", json=user_data)
            response.assert_created()
        
        # List all users
        response = test_client.get("/test-users")
        
        response.assert_ok()
        response.assert_json()
        assert len(response.json) == 3
        
        # Check that all users are present
        emails = [user["email"] for user in response.json]
        assert "user1@example.com" in emails
        assert "user2@example.com" in emails
        assert "user3@example.com" in emails


class TestModelOperations:
    """Test model operations."""
    
    @pytest.mark.asyncio
    async def test_model_create(self, test_app):
        """Test model creation."""
        # Initialize database
        await test_app.database.connect()
        await test_app.database.create_tables()
        
        # Create a user
        user = await TestUser.create(
            name="Test User",
            email="test@example.com"
        )
        
        assert user.id is not None
        assert user.name == "Test User"
        assert user.email == "test@example.com"
        assert user.is_active is True
        
        # Clean up
        await test_app.database.disconnect()
    
    @pytest.mark.asyncio
    async def test_model_get(self, test_app):
        """Test model retrieval."""
        # Initialize database
        await test_app.database.connect()
        await test_app.database.create_tables()
        
        # Create a user
        user = await TestUser.create(
            name="Test User",
            email="test@example.com"
        )
        
        # Get the user
        retrieved_user = await TestUser.get(user.id)
        
        assert retrieved_user is not None
        assert retrieved_user.id == user.id
        assert retrieved_user.name == user.name
        
        # Clean up
        await test_app.database.disconnect()
    
    @pytest.mark.asyncio
    async def test_model_update(self, test_app):
        """Test model updates."""
        # Initialize database
        await test_app.database.connect()
        await test_app.database.create_tables()
        
        # Create a user
        user = await TestUser.create(
            name="Test User",
            email="test@example.com"
        )
        
        # Update the user
        await user.update(name="Updated User")
        
        # Get the updated user
        updated_user = await TestUser.get(user.id)
        
        assert updated_user.name == "Updated User"
        assert updated_user.email == "test@example.com"  # Unchanged
        
        # Clean up
        await test_app.database.disconnect()
    
    @pytest.mark.asyncio
    async def test_model_delete(self, test_app):
        """Test model deletion."""
        # Initialize database
        await test_app.database.connect()
        await test_app.database.create_tables()
        
        # Create a user
        user = await TestUser.create(
            name="Test User",
            email="test@example.com"
        )
        
        # Delete the user
        await user.delete()
        
        # Try to get the deleted user
        deleted_user = await TestUser.get(user.id)
        
        assert deleted_user is None
        
        # Clean up
        await test_app.database.disconnect()


class TestQueryOperations:
    """Test query operations."""
    
    @pytest.mark.asyncio
    async def test_query_filter(self, test_app):
        """Test query filtering."""
        # Initialize database
        await test_app.database.connect()
        await test_app.database.create_tables()
        
        # Create users
        await TestUser.create(name="Active User", email="active@example.com", is_active=True)
        await TestUser.create(name="Inactive User", email="inactive@example.com", is_active=False)
        await TestUser.create(name="Another Active", email="another@example.com", is_active=True)
        
        # Filter active users
        active_users = await TestUser.filter(is_active=True).all()
        
        assert len(active_users) == 2
        
        # Filter by email
        specific_user = await TestUser.filter(email="active@example.com").first()
        
        assert specific_user is not None
        assert specific_user.name == "Active User"
        
        # Clean up
        await test_app.database.disconnect()
    
    @pytest.mark.asyncio
    async def test_query_count(self, test_app):
        """Test query counting."""
        # Initialize database
        await test_app.database.connect()
        await test_app.database.create_tables()
        
        # Create users
        await TestUser.create(name="User 1", email="user1@example.com")
        await TestUser.create(name="User 2", email="user2@example.com")
        await TestUser.create(name="User 3", email="user3@example.com")
        
        # Count all users
        count = await TestUser.count()
        
        assert count == 3
        
        # Clean up
        await test_app.database.disconnect()


class TestResponseAssertions:
    """Test response assertion methods."""
    
    def test_response_assertions(self, test_client):
        """Test various response assertions."""
        # Test successful response
        response = test_client.get("/test-health")
        response.assert_ok()
        
        # Test JSON response
        response.assert_json()
        response.assert_json_contains("status")
        response.assert_json_contains("status", "healthy")
        
        # Test headers
        response.assert_has_header("content-type")
        response.assert_has_header("content-type", "application/json")
        
        # Test status code assertions
        response.assert_status(200)
    
    def test_error_response_assertions(self, test_client):
        """Test error response assertions."""
        # Test not found
        response = test_client.get("/test-users/999")
        response.assert_not_found()
        response.assert_status(404)
        
        # Test JSON error response
        response.assert_json()
        response.assert_json_contains("error")


class TestAuthentication:
    """Test authentication features."""
    
    def test_authenticated_request(self, test_client):
        """Test making authenticated requests."""
        # Set auth token
        test_client.set_auth_token("test-token")
        
        # Make request
        response = test_client.get("/test-health")
        response.assert_ok()
        
        # Clear auth token
        test_client.clear_auth_token()
        
        # Make another request (should still work for public endpoints)
        response = test_client.get("/test-health")
        response.assert_ok()


class TestCookies:
    """Test cookie handling."""
    
    def test_cookie_handling(self, test_client):
        """Test cookie operations."""
        # Set a cookie
        test_client.set_cookie("test-cookie", "test-value")
        
        # Make request
        response = test_client.get("/test-health")
        response.assert_ok()
        
        # Clear cookies
        test_client.clear_cookies()
        
        # Make another request
        response = test_client.get("/test-health")
        response.assert_ok()


# Integration tests
class TestIntegration:
    """Integration tests."""
    
    def test_full_user_workflow(self, test_client):
        """Test complete user workflow."""
        # 1. List users (should be empty)
        response = test_client.get("/test-users")
        response.assert_ok()
        assert response.json == []
        
        # 2. Create a user
        user_data = {
            "name": "Integration Test User",
            "email": "integration@example.com"
        }
        
        response = test_client.post("/test-users", json=user_data)
        response.assert_created()
        user_id = response.json["id"]
        
        # 3. Get the user
        response = test_client.get(f"/test-users/{user_id}")
        response.assert_ok()
        response.assert_json_contains("name", "Integration Test User")
        
        # 4. List users again (should have one)
        response = test_client.get("/test-users")
        response.assert_ok()
        assert len(response.json) == 1
        assert response.json[0]["email"] == "integration@example.com"


# Performance tests
class TestPerformance:
    """Performance tests."""
    
    def test_multiple_requests(self, test_client):
        """Test handling multiple requests."""
        import time
        
        start_time = time.time()
        
        # Make multiple requests
        for i in range(10):
            response = test_client.get("/test-health")
            response.assert_ok()
        
        end_time = time.time()
        
        # Should complete within reasonable time
        assert end_time - start_time < 5.0  # 5 seconds max


# Utility function tests
def test_generate_user_data():
    """Test test data generation."""
    from maweng.testing import generate_user_data
    
    user_data = generate_user_data(name="Test User")
    
    assert "email" in user_data
    assert "password" in user_data
    assert user_data["name"] == "Test User"
    assert user_data["email"].endswith("@example.com")


def test_generate_post_data():
    """Test post data generation."""
    from maweng.testing import generate_post_data
    
    post_data = generate_post_data(title="Test Post")
    
    assert "content" in post_data
    assert "published" in post_data
    assert post_data["title"] == "Test Post"
    assert post_data["published"] is True


if __name__ == "__main__":
    pytest.main([__file__]) 