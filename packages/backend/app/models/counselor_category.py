"""Counselor category model for categorizing AI counselors."""
import uuid
from datetime import UTC, datetime

from sqlalchemy import Boolean, Index, String, Text, text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import Base


class CounselorCategory(Base):
    """Counselor category model for organizing AI counselors by specialty."""

    __tablename__ = 'counselor_categories'

    # Primary key
    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        server_default=text('gen_random_uuid()')
    )

    # Category information
    name: Mapped[str] = mapped_column(
        String(100),
        unique=True,
        nullable=False,
        index=True
    )
    description: Mapped[str] = mapped_column(Text, nullable=False)
    icon_name: Mapped[str] = mapped_column(String(50), nullable=False)
    
    # AI configuration
    system_prompt: Mapped[str | None] = mapped_column(Text, nullable=True)
    
    # Status
    enabled: Mapped[bool] = mapped_column(
        Boolean,
        default=True,
        nullable=False,
        index=True
    )

    # Timestamps
    created_at: Mapped[datetime] = mapped_column(
        nullable=False,
        server_default=text('CURRENT_TIMESTAMP')
    )
    updated_at: Mapped[datetime] = mapped_column(
        nullable=False,
        server_default=text('CURRENT_TIMESTAMP'),
        onupdate=datetime.now(UTC)
    )

    # Indexes
    __table_args__ = (
        Index('idx_counselor_categories_name', 'name'),
        Index('idx_counselor_categories_enabled', 'enabled'),
    )

    def __repr__(self) -> str:
        return f"<CounselorCategory(name='{self.name}', enabled={self.enabled})>"
