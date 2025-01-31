import pytest
from fastapi.testclient import TestClient
from app.main import app
from app.database import Base, engine, get_db
from sqlalchemy.orm import Session
from app.models.user import User
import os
import jwt
from datetime import datetime, timedelta

client = TestClient(app)

def setup_module(module):
    """Setup test database."""
    Base.metadata.create_all(bind=engine)

def teardown_module(module):
    """Cleanup after tests."""
    Base.metadata.drop_all(bind=engine)

def test_register_user():
    """Test user registration endpoint."""
    test_user_data = {
        "email": "test@example.com",
        "name": "Test User",
        "google_id": "test123",
        "picture": "https://example.com/pic.jpg"
    }
    response = client.post(
        "/auth/register",
        json=test_user_data
    )
    if response.status_code != 200:
        print(f"\nRegistration failed with status {response.status_code}")
        print(f"Request data: {test_user_data}")
        print(f"Response: {response.json()}")
        
    assert response.status_code == 200, f"Registration failed with response: {response.json()}"
    data = response.json()
    assert data["email"] == "test@example.com"
    assert data["google_id"] == "test123"
    assert "access_token" in data

def test_get_current_user():
    """Test getting current user info."""
    # First register a user
    register_response = client.post(
        "/auth/register",
        json={
            "email": "test2@example.com",
            "name": "Test User 2",
            "google_id": "test456",
            "picture": "https://example.com/pic2.jpg"
        }
    )
    token = register_response.json()["access_token"]
    
    # Then get user info using token
    response = client.get(
        "/auth/me",
        headers={"Authorization": f"Bearer {token}"}
    )
    assert response.status_code == 200
    data = response.json()
    assert data["email"] == "test2@example.com"

def test_invalid_token():
    """Test invalid token handling."""
    response = client.get(
        "/auth/me",
        headers={"Authorization": "Bearer invalid_token"}
    )
    assert response.status_code == 401
    assert response.json()["detail"] == "Could not validate credentials"

def test_health_check():
    """Test health check endpoint."""
    response = client.get("/auth/healthz")
    assert response.status_code == 200
    assert response.json()["status"] == "healthy"
