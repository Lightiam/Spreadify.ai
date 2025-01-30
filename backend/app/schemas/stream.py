from datetime import timezone, datetime
from pydantic import BaseModel, ConfigDict
from typing import List, Optional

class StreamBase(BaseModel):
    title: str
    description: Optional[str] = None
    platforms: List[str]
    status: Optional[str] = "draft"

class StreamCreate(StreamBase):
    pass

class StreamUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    platforms: Optional[List[str]] = None
    status: Optional[str] = None

class Stream(StreamBase):
    id: str
    user_id: str
    created_at: datetime
    updated_at: datetime
    rtmp_url: Optional[str] = None
    stream_key: Optional[str] = None

    model_config = ConfigDict(from_attributes=True)
