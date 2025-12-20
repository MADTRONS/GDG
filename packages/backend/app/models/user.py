"""User model for authentication and authorization."""
import uuid
from datetime import UTC, datetime

from sqlalchemy import Boolean, CheckConstraint, Index, String, text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import Base


class User(Base):
    """User model representing student accounts."""

    __tablename__ = 'users'

    # Primary key
    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        server_default=text('gen_random_uuid()')
    )

    # Authentication fields
    username: Mapped[str] = mapped_column(
        String(255),
        unique=True,
        nullable=False,
        index=True
    )
    password_hash: Mapped[str] = mapped_column(String(255), nullable=False)

    # Account status
    is_blocked: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)

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

    # Constraints
    __table_args__ = (
        CheckConstraint(
            r"username ~ '^\\[^\\]+\\[^\\]+$'",
            name='username_format_check'
        ),
        Index('idx_users_username', 'username'),
        Index('idx_users_is_blocked', 'is_blocked', postgresql_where=text('is_blocked = true')),
    )

    def __repr__(self) -> str:
        return f'<User(id={self.id}, username={self.username}, is_blocked={self.is_blocked})>'
