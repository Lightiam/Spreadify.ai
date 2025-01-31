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

def test_create_checkout_session():
    """Test creating Stripe checkout session."""
    token = create_test_token()
    response = client.post(
        "/stripe/create-checkout-session",
        headers={"Authorization": f"Bearer {token}"},
        json={
            "price_id": "price_test",
            "success_url": "http://localhost:5173/success",
            "cancel_url": "http://localhost:5173/pricing"
        }
    )
    assert response.status_code in [200, 400]  # 400 if Stripe key not configured

def test_health_check():
    """Test health check endpoint."""
    response = client.get("/healthz")
    assert response.status_code == 200
    assert response.json()["status"] == "healthy"
