
"""Pydantic request and response schemas used by FastAPI endpoints."""
from pydantic import BaseModel, Field
from typing import Optional, Dict, Any
from datetime import datetime

class CallCreate(BaseModel):
    """Schema for creating a new call record."""
    call_id: str = Field(..., description="External unique call identifier")
    caller: Optional[str] = None
    callee: Optional[str] = None
    start_time: Optional[datetime] = None
    end_time: Optional[datetime] = None
    duration: Optional[int] = None

class CallRead(BaseModel):
    """Schema returned when listing call records."""
    id: int
    call_id: str
    caller: Optional[str]
    callee: Optional[str]
    start_time: Optional[datetime]
    end_time: Optional[datetime]
    duration: Optional[int]
    is_processed: bool
    recording_file: Optional[str]

    class Config:
        orm_mode = True

class InsightRead(BaseModel):
    """Schema returned for call insights."""
    transcription: Optional[str]
    sentiment: Optional[str]
    keywords: Optional[Dict[str, Any]]
    summary: Optional[str]
    created_at: Optional[datetime]

    class Config:
        orm_mode = True
