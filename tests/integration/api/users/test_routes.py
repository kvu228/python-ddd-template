"""Integration tests for user API routes."""

from fastapi.testclient import TestClient

from src.main import app

client = TestClient(app)


def test_health_check():
    """Test health check endpoint."""
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json()["status"] == "healthy"


def test_register_user():
    """Test user registration."""
    response = client.post(
        "/api/v1/users/register",
        json={"email": "test@example.com", "name": "Test User"},
    )
    assert response.status_code == 201
    data = response.json()
    assert data["email"] == "test@example.com"
    assert data["name"] == "Test User"
    assert "id" in data


def test_get_user_not_found():
    """Test getting non-existent user."""
    from uuid import uuid4

    response = client.get(f"/api/v1/users/{uuid4()}")
    assert response.status_code == 404


