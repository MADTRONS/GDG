"""Admin user management router."""
import secrets
import uuid
from datetime import UTC, datetime

from fastapi import APIRouter, Depends, HTTPException, Query, Request, status
from pydantic import BaseModel, EmailStr
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.models.admin import Admin, AdminRole
from app.models.audit_log import AuditAction
from app.utils.admin_dependencies import require_admin_role
from app.utils.audit import create_audit_log
from app.utils.security import hash_password

admin_users_router = APIRouter(
    prefix="/api/admin/users",
    tags=["admin-users"]
)


class AdminUserResponse(BaseModel):
    """Response schema for admin user."""
    id: str
    email: str
    role: str
    is_active: bool
    last_login_at: str | None
    created_at: str


class CreateAdminRequest(BaseModel):
    """Request schema for creating admin user."""
    email: EmailStr
    role: str


class CreateAdminResponse(BaseModel):
    """Response schema for created admin user."""
    id: str
    email: str
    role: str
    temporary_password: str


class UpdateAdminRequest(BaseModel):
    """Request schema for updating admin user."""
    role: str | None = None
    is_active: bool | None = None


class PasswordResetRequest(BaseModel):
    """Request schema for password reset."""
    current_password: str | None = None
    new_password: str
    admin_id: str | None = None


def generate_temp_password() -> str:
    """Generate secure temporary password (16 characters)."""
    return secrets.token_urlsafe(16)


@admin_users_router.get("", response_model=list[AdminUserResponse])
async def list_admin_users(
    current_admin: dict = Depends(require_admin_role(AdminRole.SUPER_ADMIN)),
    db: AsyncSession = Depends(get_db)
) -> list[AdminUserResponse]:
    """
    List all admin users (SUPER_ADMIN only).
    
    Returns list of all admin users with their details.
    """
    try:
        query = select(Admin).order_by(Admin.created_at.desc())
        result = await db.execute(query)
        admins = result.scalars().all()
        
        return [
            AdminUserResponse(
                id=str(admin.id),
                email=admin.email,
                role=admin.role.value,
                is_active=admin.is_active,
                last_login_at=admin.last_login_at.isoformat() if admin.last_login_at else None,
                created_at=admin.created_at.isoformat()
            )
            for admin in admins
        ]
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to fetch admin users: {str(e)}"
        )


@admin_users_router.post("", response_model=CreateAdminResponse, status_code=status.HTTP_201_CREATED)
async def create_admin_user(
    data: CreateAdminRequest,
    request: Request,
    current_admin: dict = Depends(require_admin_role(AdminRole.SUPER_ADMIN)),
    db: AsyncSession = Depends(get_db)
) -> CreateAdminResponse:
    """
    Create new admin user (SUPER_ADMIN only).
    
    Creates a new admin user with a temporary password.
    The temporary password is returned in the response and should be securely
    communicated to the new admin.
    """
    try:
        # Validate role
        try:
            admin_role = AdminRole(data.role.upper())
        except ValueError:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Invalid role. Must be one of: {', '.join([r.value for r in AdminRole])}"
            )
        
        # Check if email already exists
        email_lower = data.email.lower()
        existing_query = select(Admin).where(Admin.email == email_lower)
        existing_result = await db.execute(existing_query)
        if existing_result.scalar_one_or_none():
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email already exists"
            )
        
        # Generate temporary password
        temp_password = generate_temp_password()
        password_hash_value = hash_password(temp_password)
        
        # Create admin
        new_admin = Admin(
            email=email_lower,
            password_hash=password_hash_value,
            role=admin_role,
            is_active=True
        )
        
        db.add(new_admin)
        await db.flush()
        
        # Create audit log
        await create_audit_log(
            db=db,
            admin_user_id=uuid.UUID(current_admin['admin_id']),
            action=AuditAction.CREATE,
            resource_type='admin_user',
            resource_id=new_admin.id,
            details={'email': new_admin.email, 'role': new_admin.role.value},
            ip_address=request.client.host if request.client else None
        )
        
        await db.commit()
        await db.refresh(new_admin)
        
        return CreateAdminResponse(
            id=str(new_admin.id),
            email=new_admin.email,
            role=new_admin.role.value,
            temporary_password=temp_password
        )
    except HTTPException:
        await db.rollback()
        raise
    except Exception as e:
        await db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to create admin user: {str(e)}"
        )


@admin_users_router.put("/{admin_id}")
async def update_admin_user(
    admin_id: str,
    data: UpdateAdminRequest,
    request: Request,
    current_admin: dict = Depends(require_admin_role(AdminRole.SUPER_ADMIN)),
    db: AsyncSession = Depends(get_db)
) -> dict:
    """
    Update admin user role or active status (SUPER_ADMIN only).
    
    Allows updating role and/or is_active status of an admin user.
    """
    try:
        # Validate UUID
        try:
            admin_uuid = uuid.UUID(admin_id)
        except ValueError:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid admin ID format"
            )
        
        # Validate role if provided
        if data.role is not None:
            try:
                new_role = AdminRole(data.role.upper())
            except ValueError:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Invalid role. Must be one of: {', '.join([r.value for r in AdminRole])}"
                )
        else:
            new_role = None
        
        # Fetch admin
        query = select(Admin).where(Admin.id == admin_uuid)
        result = await db.execute(query)
        admin = result.scalar_one_or_none()
        
        if not admin:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Admin user not found"
            )
        
        # Track changes for audit log
        changes = {}
        
        # Update role
        if new_role is not None and admin.role != new_role:
            old_role = admin.role.value
            admin.role = new_role
            changes['role'] = {'old': old_role, 'new': new_role.value}
        
        # Update active status
        if data.is_active is not None and admin.is_active != data.is_active:
            changes['is_active'] = {'old': admin.is_active, 'new': data.is_active}
            admin.is_active = data.is_active
        
        if not changes:
            return {"message": "No changes made"}
        
        # Create audit log
        await create_audit_log(
            db=db,
            admin_user_id=uuid.UUID(current_admin['admin_id']),
            action=AuditAction.UPDATE,
            resource_type='admin_user',
            resource_id=admin.id,
            details={'email': admin.email, 'changes': changes},
            ip_address=request.client.host if request.client else None
        )
        
        await db.commit()
        
        return {"message": "Admin user updated successfully"}
    except HTTPException:
        await db.rollback()
        raise
    except Exception as e:
        await db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to update admin user: {str(e)}"
        )


@admin_users_router.delete("/{admin_id}")
async def deactivate_admin_user(
    admin_id: str,
    request: Request,
    current_admin: dict = Depends(require_admin_role(AdminRole.SUPER_ADMIN)),
    db: AsyncSession = Depends(get_db)
) -> dict:
    """
    Deactivate admin user (soft delete, SUPER_ADMIN only).
    
    Sets is_active to False. Prevents admin from deactivating themselves.
    """
    try:
        # Validate UUID
        try:
            admin_uuid = uuid.UUID(admin_id)
        except ValueError:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid admin ID format"
            )
        
        # Prevent self-deactivation
        current_admin_id = uuid.UUID(current_admin['admin_id'])
        if admin_uuid == current_admin_id:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Cannot deactivate your own account"
            )
        
        # Fetch admin
        query = select(Admin).where(Admin.id == admin_uuid)
        result = await db.execute(query)
        admin = result.scalar_one_or_none()
        
        if not admin:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Admin user not found"
            )
        
        if not admin.is_active:
            return {"message": "Admin user already inactive"}
        
        # Deactivate
        admin.is_active = False
        
        # Create audit log
        await create_audit_log(
            db=db,
            admin_user_id=current_admin_id,
            action=AuditAction.DELETE,
            resource_type='admin_user',
            resource_id=admin.id,
            details={'email': admin.email, 'action': 'deactivated'},
            ip_address=request.client.host if request.client else None
        )
        
        await db.commit()
        
        return {"message": "Admin user deactivated successfully"}
    except HTTPException:
        await db.rollback()
        raise
    except Exception as e:
        await db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to deactivate admin user: {str(e)}"
        )