from datetime import timezone
import pytest
from fastapi import status
from app.schemas.auth import UserCreate

def test_google_login_redirect(client):
    """Test that Google login endpoint redirects to Google OAuth."""
    state = "test_state"
    response = client.get(f"/auth/login/google?state={state}", follow_redirects=False)
    assert response.status_code == status.HTTP_302_FOUND
    assert "accounts.google.com" in response.headers["location"]

def test_get_current_user(authorized_client, test_user):
    """Test getting current user info with valid token."""
    response = authorized_client.get("/auth/me")
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert data["email"] == test_user.email

def test_get_current_user_unauthorized(client):
    """Test getting current user info without token."""
    response = client.get("/auth/me")
    assert response.status_code == status.HTTP_401_UNAUTHORIZED

def test_get_test_token(client):
    """Test getting a test token for WebSocket testing."""
    response = client.get("/auth/test-token")
    assert response.status_code == status.HTTP_200_OK
    assert isinstance(response.json(), str)  # Should return a JWT string
