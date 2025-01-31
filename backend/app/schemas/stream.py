from pydantic import BaseModel
from datetime import datetime
from typing import Optional

class StreamBase(BaseModel):
    """Base stream schema."""
    title: str
    description: str
    platform: str  # youtube, twitch, facebook, etc.

class StreamCreate(StreamBase):
    """Schema for creating a stream."""
    pass

class StreamResponse(StreamBase):
    """Schema for stream response."""
    id: int
    user_id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True
