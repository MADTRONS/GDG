"""Admin user model for administrative authentication and authorization."""
import enum
import uuid
from datetime import UTC, datetime

from sqlalchemy import Boolean, Enum, Index, String, text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import Base


class AdminRole(str, enum.Enum):
    """Admin role enumeration defining access levels."""

    SUPER_ADMIN = 'SUPER_ADMIN'
    SYSTEM_MONITOR = 'SYSTEM_MONITOR'
    CONTENT_MANAGER = 'CONTENT_MANAGER'


class Admin(Base):
    """Admin user model for system administration."""

    __tablename__ = 'admin_users'

    # Primary key
    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        server_default=text('gen_random_uuid()')
    )

    # Authentication fields
    email: Mapped[str] = mapped_column(
        String(255),
        unique=True,
        nullable=False
    )
    password_hash: Mapped[str] = mapped_column(String(255), nullable=False)

    # Authorization
    role: Mapped[AdminRole] = mapped_column(
        Enum(AdminRole),
        nullable=False,
        default=AdminRole.CONTENT_MANAGER
    )

    # Account status
    is_active: Mapped[bool] = mapped_column(
        Boolean,
        default=True,
        nullable=False
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
    last_login_at: Mapped[datetime | None] = mapped_column(nullable=True)

    # Indexes
    __table_args__ = (
        Index('ix_admin_users_email', 'email', unique=True),
        Index('ix_admin_users_is_active', 'is_active'),
    )

    def __repr__(self) -> str:
        """String representation of Admin."""
        return f'<Admin {self.email} ({self.role.value})>'
