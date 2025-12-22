"""Session-related Pydantic schemas."""
from datetime import datetime
from typing import Any, Optional
from uuid import UUID

from pydantic import BaseModel, Field, field_validator


class TranscriptMessage(BaseModel):
    """Schema for a single transcript message."""
    timestamp: str  # ISO 8601 format
    speaker: str    # "user" or "bot"
    text: str

    @field_validator('speaker')
    @classmethod
    def validate_speaker(cls, v: str) -> str:
        if v not in ['user', 'bot']:
            raise ValueError('speaker must be "user" or "bot"')
        return v


class SaveSessionRequest(BaseModel):
    """Request schema for saving session data."""
    session_id: UUID
    transcript: list[TranscriptMessage]
    duration: int = Field(..., ge=0, description="Duration in seconds")
    crisis_detected: bool = False


class SaveSessionResponse(BaseModel):
    """Response schema after saving session."""
    success: bool
    session_id: UUID
    message: str


class SessionStatsResponse(BaseModel):
    """Response schema for session statistics."""
    total_sessions: int
    total_hours: float
    top_category: Optional[str] = None
    top_category_icon: Optional[str] = None
    last_session_date: Optional[str] = None


class SessionSummary(BaseModel):
    """Summary of a counseling session."""
    session_id: UUID
    counselor_category: str
    mode: str
    started_at: datetime
    ended_at: Optional[datetime]
    duration_seconds: Optional[int]
    crisis_detected: bool

    class Config:
        from_attributes = True


class SessionDetail(BaseModel):
    """Detailed session information including transcript."""
    session_id: UUID
    counselor_category: str
    counselor_icon: str
    mode: str
    started_at: str  # ISO format
    ended_at: Optional[str]  # ISO format
    duration_seconds: Optional[int]
    transcript: Optional[list[dict[str, str]]]
    quality_metrics: Optional[dict[str, Any]] = None
    crisis_detected: bool


class SessionPreview(BaseModel):
    """Session preview for list display."""
    session_id: str
    counselor_category: str
    counselor_icon: str
    mode: str
    started_at: str  # ISO format
    duration_seconds: int
    transcript_preview: str


class SessionsListResponse(BaseModel):
    """Paginated response for session history list."""
    sessions: list[SessionPreview]
    total_count: int
    page: int
    limit: int
