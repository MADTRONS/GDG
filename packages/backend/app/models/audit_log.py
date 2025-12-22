"""Audit log model for tracking admin actions."""
import enum
import uuid
from datetime import UTC, datetime

from sqlalchemy import Enum, ForeignKey, Index, String, Text, text
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import Base


class AuditAction(str, enum.Enum):
    """Audit action types."""
    
    CREATE = 'CREATE'
    UPDATE = 'UPDATE'
    DELETE = 'DELETE'
    LOGIN = 'LOGIN'
    LOGOUT = 'LOGOUT'


class AuditLog(Base):
    """Audit log model for tracking admin actions."""

    __tablename__ = 'audit_log'

    # Primary key
    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        server_default=text('gen_random_uuid()')
    )

    # Admin reference
    admin_user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey('admin_users.id', ondelete='CASCADE'),
        nullable=False
    )

    # Action details
    action: Mapped[AuditAction] = mapped_column(
        Enum(AuditAction),
        nullable=False
    )
    resource_type: Mapped[str] = mapped_column(String(50), nullable=False)
    resource_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True),
        nullable=True
    )
    details: Mapped[dict | None] = mapped_column(JSONB, nullable=True)
    ip_address: Mapped[str | None] = mapped_column(String(45), nullable=True)

    # Timestamp
    timestamp: Mapped[datetime] = mapped_column(
        nullable=False,
        server_default=text('CURRENT_TIMESTAMP')
    )

    # Indexes
    __table_args__ = (
        Index('idx_audit_log_admin_user_id', 'admin_user_id'),
        Index('idx_audit_log_timestamp', 'timestamp'),
        Index('idx_audit_log_resource', 'resource_type', 'resource_id'),
    )

    def __repr__(self) -> str:
        return f"<AuditLog {self.action.value} {self.resource_type} by {self.admin_user_id}>"
