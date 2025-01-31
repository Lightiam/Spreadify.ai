import pytest
from fastapi.testclient import TestClient
from app.main import app
from app.database import Base, engine
import jwt
import os
from datetime import datetime, timedelta

client = TestClient(app)

def setup_module(module):
    """Setup test database."""
    Base.metadata.create_all(bind=engine)

def teardown_module(module):
    """Cleanup after tests."""
    Base.metadata.drop_all(bind=engine)

def create_test_token():
    """Create a test JWT token."""
    # First register a test user
    response = client.post(
        "/auth/register",
        json={
            "email": "test@example.com",
            "name": "Test User",
            "google_id": "test123",
            "picture": "https://example.com/pic.jpg"
        }
    )
    assert response.status_code == 200, f"Registration failed with response: {response.json()}"
    data = response.json()
    assert "access_token" in data, "Token not found in response"
    return data["access_token"]

def test_create_stream():
    """Test stream creation endpoint."""
    token = create_test_token()
    response = client.post(
        "/streams/",
        headers={"Authorization": f"Bearer {token}"},
        json={
            "title": "Test Stream",
            "description": "Test Description",
            "platform": "youtube"
        }
    )
    assert response.status_code == 200
    data = response.json()
    assert data["title"] == "Test Stream"
    assert data["platform"] == "youtube"

def test_list_streams():
    """Test listing streams endpoint."""
    # First register a test user and create a stream
    token = create_test_token()
    
    # Create a test stream first
    create_response = client.post(
        "/streams/",
        headers={"Authorization": f"Bearer {token}"},
        json={
            "title": "Test Stream",
            "description": "Test Description",
            "platform": "youtube"
        }
    )
    assert create_response.status_code == 200
    
    # Then list streams
    list_response = client.get(
        "/streams/",
        headers={"Authorization": f"Bearer {token}"}
    )
    assert list_response.status_code == 200
    streams = list_response.json()
    assert isinstance(streams, list)
    assert len(streams) > 0
    assert streams[0]["title"] == "Test Stream"
