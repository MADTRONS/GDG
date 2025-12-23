"""Admin audit log router."""
from datetime import UTC, datetime
from typing import Any
import uuid

from fastapi import APIRouter, Depends, HTTPException, Query, status
from pydantic import BaseModel
from sqlalchemy import and_, func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.models.admin import Admin, AdminRole
from app.models.audit_log import AuditAction, AuditLog
from app.utils.admin_dependencies import require_admin_role

admin_audit_router = APIRouter(
    prefix="/api/admin/audit-log",
    tags=["admin-audit"]
)


class AuditLogEntry(BaseModel):
    """Response schema for a single audit log entry."""
    id: str
    admin_email: str
    action: str
    resource_type: str
    resource_id: str | None
    details: dict[str, Any]
    ip_address: str | None
    timestamp: str


class AuditLogResponse(BaseModel):
    """Response schema for paginated audit log."""
    logs: list[AuditLogEntry]
    total_count: int
    page: int
    limit: int
    total_pages: int


@admin_audit_router.get("", response_model=AuditLogResponse)
async def get_audit_log(
    admin_user_id: str | None = Query(None, description="Filter by admin user ID"),
    action: str | None = Query(None, description="Filter by action type"),
    resource_type: str | None = Query(None, description="Filter by resource type"),
    start_date: str | None = Query(None, description="Start date (YYYY-MM-DD)"),
    end_date: str | None = Query(None, description="End date (YYYY-MM-DD)"),
    page: int = Query(1, ge=1, description="Page number"),
    limit: int = Query(50, ge=1, le=100, description="Items per page"),
    current_admin: dict = Depends(require_admin_role(AdminRole.SUPER_ADMIN)),
    db: AsyncSession = Depends(get_db)
) -> AuditLogResponse:
    """
    Get audit log entries with filtering and pagination.
    
    Only accessible by SUPER_ADMIN role.
    Audit logs are immutable and cannot be deleted.
    """
    try:
        # Build filters
        filters = []
        
        if admin_user_id:
            try:
                admin_uuid = uuid.UUID(admin_user_id)
                filters.append(AuditLog.admin_user_id == admin_uuid)
            except ValueError:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Invalid admin_user_id format"
                )
        
        if action:
            try:
                action_enum = AuditAction(action.upper())
                filters.append(AuditLog.action == action_enum)
            except ValueError:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Invalid action. Must be one of: {', '.join([a.value for a in AuditAction])}"
                )
        
        if resource_type:
            filters.append(AuditLog.resource_type == resource_type)
        
        if start_date:
            try:
                start_dt = datetime.strptime(start_date, "%Y-%m-%d").replace(tzinfo=UTC)
                filters.append(AuditLog.timestamp >= start_dt)
            except ValueError:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Invalid start_date format. Use YYYY-MM-DD"
                )
        
        if end_date:
            try:
                end_dt = datetime.strptime(end_date, "%Y-%m-%d").replace(
                    hour=23, minute=59, second=59, tzinfo=UTC
                )
                filters.append(AuditLog.timestamp <= end_dt)
            except ValueError:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Invalid end_date format. Use YYYY-MM-DD"
                )
        
        # Count query
        count_query = select(func.count(AuditLog.id))
        if filters:
            count_query = count_query.where(and_(*filters))
        
        count_result = await db.execute(count_query)
        total_count = count_result.scalar() or 0
        
        # Calculate total pages
        total_pages = (total_count + limit - 1) // limit if total_count > 0 else 0
        
        # Data query with join to Admin for email
        query = (
            select(AuditLog, Admin.email)
            .join(Admin, AuditLog.admin_user_id == Admin.id)
            .order_by(AuditLog.timestamp.desc())
            .offset((page - 1) * limit)
            .limit(limit)
        )
        
        if filters:
            query = query.where(and_(*filters))
        
        result = await db.execute(query)
        rows = result.all()
        
        logs = [
            AuditLogEntry(
                id=str(log.id),
                admin_email=email,
                action=log.action.value,
                resource_type=log.resource_type,
                resource_id=str(log.resource_id) if log.resource_id else None,
                details=log.details or {},
                ip_address=log.ip_address,
                timestamp=log.timestamp.isoformat()
            )
            for log, email in rows
        ]
        
        return AuditLogResponse(
            logs=logs,
            total_count=total_count,
            page=page,
            limit=limit,
            total_pages=total_pages
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to fetch audit log: {str(e)}"
        )