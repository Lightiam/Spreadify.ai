import pytest
from fastapi import status
from app.schemas.auth import UserCreate
import stripe

def test_create_checkout_session(authorized_client):
    """Test creating a Stripe checkout session."""
    response = authorized_client.post(
        "/stripe/create-checkout-session",
        json={"priceId": "price_H5ggYwtDq4fbrJ"}
    )
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert "url" in data
    assert data["url"].startswith("https://checkout.stripe.com/")

def test_create_checkout_session_unauthorized(client):
    """Test creating a checkout session without auth."""
    response = client.post(
        "/stripe/create-checkout-session",
        json={"priceId": "price_H5ggYwtDq4fbrJ"}
    )
    assert response.status_code == status.HTTP_401_UNAUTHORIZED

def test_webhook_signature_verification(client):
    """Test Stripe webhook signature verification."""
    # Create a mock webhook event
    payload = {
        "type": "checkout.session.completed",
        "data": {
            "object": {
                "customer": "cus_123",
                "subscription": "sub_123"
            }
        }
    }
    
    # Test without signature (should fail)
    response = client.post("/stripe/webhook", json=payload)
    assert response.status_code == status.HTTP_400_BAD_REQUEST

def test_success_page(authorized_client):
    """Test success page endpoint."""
    response = authorized_client.get("/stripe/success?session_id=cs_test_123")
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert "status" in data
    assert data["status"] == "success"
