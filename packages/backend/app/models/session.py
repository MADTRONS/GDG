"""Session model for tracking counseling sessions."""
import uuid
from datetime import UTC, datetime
from typing import Any, Optional

from sqlalchemy import Boolean, ForeignKey, Index, String, text
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import Base


class Session(Base):
    """Session model for tracking voice and video counseling sessions."""

    __tablename__ = "sessions"

    # Primary key
    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        server_default=text("gen_random_uuid()")
    )

    # Foreign keys
    user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True
    )

    # Session information
    counselor_category: Mapped[str] = mapped_column(
        String(100),
        nullable=False,
        index=True
    )
    mode: Mapped[str] = mapped_column(
        String(20),
        nullable=False,
        index=True  # "voice" or "video"
    )
    room_name: Mapped[str] = mapped_column(
        String(100),
        nullable=False,
        unique=True
    )
    
    # Session data
    transcript: Mapped[Optional[dict[str, Any]]] = mapped_column(JSONB, nullable=True)
    duration_seconds: Mapped[Optional[int]] = mapped_column(nullable=True)
    crisis_detected: Mapped[bool] = mapped_column(
        Boolean,
        nullable=False,
        server_default=text("false")
    )
    
    # Timestamps
    started_at: Mapped[datetime] = mapped_column(
        nullable=False,
        server_default=text("CURRENT_TIMESTAMP"),
        index=True
    )
    ended_at: Mapped[Optional[datetime]] = mapped_column(nullable=True)

    # Indexes
    __table_args__ = (
        Index("idx_sessions_user_started", "user_id", "started_at"),
        Index("idx_sessions_category", "counselor_category"),
        Index("idx_sessions_mode", "mode"),
    )

    def __repr__(self) -> str:
        return f"<Session(id='{self.id}', user_id='{self.user_id}', mode='{self.mode}')>"
