from datetime import timezone
import pytest
from fastapi import status
from fastapi.testclient import TestClient
import json

def test_websocket_connection(client):
    """Test WebSocket connection with valid token."""
    # First get a test token
    token_response = client.get("/auth/test-token")
    assert token_response.status_code == status.HTTP_200_OK
    token = token_response.json()
    
    # Then try to connect to WebSocket with room ID
    room_id = "test-room"
    with client.websocket_connect(f"/webrtc/signal/{room_id}?token={token}") as websocket:
        # Should receive connection success message
        response = websocket.receive_json()
        assert response["type"] == "connection-success"
        
        # Test message exchange
        test_message = {
            "type": "test",
            "from": "test-peer",
            "data": "Hello WebSocket"
        }
        websocket.send_json(test_message)
        
        # Should receive test response
        response = websocket.receive_json()
        assert response["type"] == "test-response"
        assert response["from"] == "server"
        assert response["to"] == "test-peer"
        assert "Server received your test message" in response["data"]

def test_websocket_unauthorized(client):
    with pytest.raises(Exception):
        with client.websocket_connect("/webrtc/signal"):
            pass  # Should not reach here

def test_websocket_invalid_token(client):
    with pytest.raises(Exception):
        with client.websocket_connect("/webrtc/signal?token=invalid"):
            pass  # Should not reach here
