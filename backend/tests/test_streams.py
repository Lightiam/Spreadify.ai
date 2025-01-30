import pytest
from fastapi import status
from datetime import datetime, timezone
from app.schemas.stream import StreamCreate, StreamUpdate
from uuid import uuid4

@pytest.fixture
def test_stream_data():
    return {
        "title": "Test Stream",
        "description": "Test Description",
        "platforms": ["youtube", "twitch"],
        "status": "draft"
    }

@pytest.fixture
def test_stream(authorized_client, test_stream_data):
    response = authorized_client.post("/streams/", json=test_stream_data)
    return response.json()

def test_create_stream(authorized_client, test_stream_data):
    """Test creating a new stream."""
    response = authorized_client.post("/streams/", json=test_stream_data)
    assert response.status_code == status.HTTP_201_CREATED
    data = response.json()
    assert data["title"] == test_stream_data["title"]
    assert data["description"] == test_stream_data["description"]
    assert data["platforms"] == test_stream_data["platforms"]
    assert data["status"] == test_stream_data["status"]
    assert "id" in data
    assert "created_at" in data
    assert "updated_at" in data

def test_create_stream_unauthorized(client, test_stream_data):
    """Test creating a stream without auth."""
    response = client.post("/streams/", json=test_stream_data)
    assert response.status_code == status.HTTP_401_UNAUTHORIZED

def test_get_streams(authorized_client, test_stream):
    """Test getting all streams for a user."""
    response = authorized_client.get("/streams/")
    assert response.status_code == status.HTTP_200_OK
    streams = response.json()
    assert isinstance(streams, list)
    assert len(streams) >= 1
    assert any(s["id"] == test_stream["id"] for s in streams)

def test_get_stream(authorized_client, test_stream):
    """Test getting a specific stream."""
    response = authorized_client.get(f"/streams/{test_stream['id']}")
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert data["id"] == test_stream["id"]
    assert data["title"] == test_stream["title"]

def test_get_nonexistent_stream(authorized_client):
    """Test getting a stream that doesn't exist."""
    response = authorized_client.get(f"/streams/{uuid4()}")
    assert response.status_code == status.HTTP_404_NOT_FOUND

def test_update_stream(authorized_client, test_stream):
    """Test updating a stream."""
    update_data = {
        "title": "Updated Stream",
        "description": "Updated Description",
        "platforms": ["youtube", "facebook"],
        "status": "live"
    }
    response = authorized_client.patch(f"/streams/{test_stream['id']}", json=update_data)
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert data["title"] == update_data["title"]
    assert data["description"] == update_data["description"]
    assert data["platforms"] == update_data["platforms"]
    assert data["status"] == update_data["status"]
    assert datetime.fromisoformat(data["updated_at"]) > datetime.fromisoformat(test_stream["updated_at"])

def test_update_stream_not_found(authorized_client):
    """Test updating a nonexistent stream."""
    response = authorized_client.patch(
        f"/streams/{uuid4()}",
        json={"title": "Updated Stream"}
    )
    assert response.status_code == status.HTTP_404_NOT_FOUND

def test_delete_stream(authorized_client, test_stream):
    """Test deleting a stream."""
    response = authorized_client.delete(f"/streams/{test_stream['id']}")
    assert response.status_code == status.HTTP_204_NO_CONTENT
    
    # Verify it's gone
    get_response = authorized_client.get(f"/streams/{test_stream['id']}")
    assert get_response.status_code == status.HTTP_404_NOT_FOUND

def test_delete_stream_not_found(authorized_client):
    """Test deleting a nonexistent stream."""
    response = authorized_client.delete(f"/streams/{uuid4()}")
    assert response.status_code == status.HTTP_404_NOT_FOUND
