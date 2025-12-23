"""Audit logging utilities."""
import uuid
from typing import Any

from sqlalchemy.ext.asyncio import AsyncSession

from app.models.audit_log import AuditAction, AuditLog


async def create_audit_log(
    db: AsyncSession,
    admin_user_id: uuid.UUID,
    action: AuditAction,
    resource_type: str,
    resource_id: uuid.UUID | None = None,
    details: dict[str, Any] | None = None,
    ip_address: str | None = None
) -> AuditLog:
    """
    Create an audit log entry.
    
    Args:
        db: Database session
        admin_user_id: ID of the admin performing the action
        action: Type of action (CREATE, UPDATE, DELETE, LOGIN, LOGOUT)
        resource_type: Type of resource being acted upon
        resource_id: Optional ID of the specific resource
        details: Optional additional details as JSON
        ip_address: Optional IP address of the admin
    
    Returns:
        The created AuditLog entry
    """
    audit_entry = AuditLog(
        admin_user_id=admin_user_id,
        action=action,
        resource_type=resource_type,
        resource_id=resource_id,
        details=details or {},
        ip_address=ip_address
    )
    db.add(audit_entry)
    await db.flush()  # Don't commit, let caller decide
    return audit_entry