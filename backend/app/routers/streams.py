from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.database import get_db
from app.dependencies import get_current_user
from app.models.user import User
from app.schemas.stream import StreamCreate, StreamResponse

router = APIRouter(tags=["streams"])

@router.post("/", response_model=StreamResponse)
async def create_stream(
    stream: StreamCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Create a new stream."""
    return {
        "id": 1,  # Placeholder ID for testing
        "title": stream.title,
        "description": stream.description,
        "platform": stream.platform,
        "user_id": current_user.id,
        "created_at": "2024-01-31T00:00:00Z",
        "updated_at": "2024-01-31T00:00:00Z"
    }

@router.get("/", response_model=list[StreamResponse])
async def list_streams(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """List all streams for the current user."""
    # For now, return a mock stream since we haven't implemented stream storage yet
    return [{
        "id": 1,
        "title": "Test Stream",
        "description": "Test Description",
        "platform": "youtube",
        "user_id": current_user.id,
        "created_at": "2024-01-31T00:00:00Z",
        "updated_at": "2024-01-31T00:00:00Z"
    }]

@router.get("/healthz")
async def health_check():
    return {"status": "healthy"}
