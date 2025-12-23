"""Admin authentication router for login/logout endpoints."""
from datetime import UTC, datetime
import uuid

from fastapi import APIRouter, Depends, HTTPException, Response, status
from pydantic import BaseModel, EmailStr
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.config import get_settings
from app.database import get_db
from app.models.admin import Admin, AdminRole
from app.utils.admin_dependencies import get_current_admin, require_admin_role
from app.utils.admin_jwt import create_admin_access_token
from app.utils.security import hash_password, verify_password

admin_auth_router = APIRouter(prefix='/api/admin/auth', tags=['admin-authentication'])


class AdminLoginRequest(BaseModel):
    """Admin login request schema."""

    email: EmailStr
    password: str


class AdminLoginResponse(BaseModel):
    """Admin login response schema."""

    email: str
    role: str
    message: str


@admin_auth_router.post('/login', response_model=AdminLoginResponse)
async def admin_login(
    credentials: AdminLoginRequest,
    response: Response,
    db: AsyncSession = Depends(get_db)
) -> AdminLoginResponse:
    """
    Authenticate admin user and return JWT token.

    Args:
        credentials: Admin login credentials (email and password)
        response: FastAPI response object for setting cookies
        db: Database session

    Returns:
        AdminLoginResponse with admin data

    Raises:
        HTTPException 401: Invalid credentials or admin not found
        HTTPException 403: Admin account is inactive
    """
    # Query database for admin user
    query = select(Admin).where(
        Admin.email == credentials.email.lower()
    )
    result = await db.execute(query)
    admin = result.scalar_one_or_none()

    # Check if admin exists
    if admin is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail='Invalid email or password'
        )

    # Check if admin is active
    if not admin.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail='Your admin account has been deactivated'
        )

    # Verify password
    if not verify_password(credentials.password, admin.password_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail='Invalid email or password'
        )

    # Update last login timestamp
    admin.last_login_at = datetime.now(UTC)
    await db.commit()

    # Generate JWT token
    access_token = create_admin_access_token(
        admin_id=admin.id,
        email=admin.email,
        role=admin.role.value
    )

    # Set httpOnly cookie
    settings = get_settings()
    response.set_cookie(
        key='admin_token',
        value=access_token,
        httponly=True,
        secure=settings.environment == 'production',
        samesite='lax',
        max_age=28800  # 8 hours in seconds
    )

    # Return response
    return AdminLoginResponse(
        email=admin.email,
        role=admin.role.value,
        message='Login successful'
    )


@admin_auth_router.post('/logout')
async def admin_logout(
    response: Response,
    current_admin: dict = Depends(get_current_admin)
) -> dict:
    """
    Log out admin by clearing authentication cookie.

    Args:
        response: FastAPI response object for clearing cookies
        current_admin: Current authenticated admin from JWT token

    Returns:
        Success message
    """
    response.delete_cookie(key='admin_token')
    return {'message': 'Logout successful'}


@admin_auth_router.put('/reset-password')
async def reset_password(
    current_password: str,
    new_password: str,
    current_admin: dict = Depends(get_current_admin),
    db: AsyncSession = Depends(get_db)
) -> dict:
    """
    Reset own password.
    
    Allows an admin to change their own password by providing current password.
    
    Args:
        current_password: Current password for verification
        new_password: New password to set
        current_admin: Current authenticated admin
        db: Database session
    
    Returns:
        Success message
    
    Raises:
        HTTPException 401: Current password is incorrect
        HTTPException 400: Invalid new password
    """
    # Validate new password length
    if len(new_password) < 8:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail='New password must be at least 8 characters'
        )
    
    # Fetch admin from database
    admin_id = uuid.UUID(current_admin['admin_id'])
    query = select(Admin).where(Admin.id == admin_id)
    result = await db.execute(query)
    admin = result.scalar_one_or_none()
    
    if not admin:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail='Admin user not found'
        )
    
    # Verify current password
    if not verify_password(current_password, admin.password_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail='Current password is incorrect'
        )
    
    # Set new password
    admin.password_hash = hash_password(new_password)
    await db.commit()
    
    return {'message': 'Password reset successful'}


@admin_auth_router.put('/force-reset-password/{admin_id}')
async def force_reset_password(
    admin_id: str,
    new_password: str,
    current_admin: dict = Depends(require_admin_role(AdminRole.SUPER_ADMIN)),
    db: AsyncSession = Depends(get_db)
) -> dict:
    """
    Force reset password for another admin user (SUPER_ADMIN only).
    
    Allows super admins to reset passwords for other admin users.
    
    Args:
        admin_id: ID of admin user to reset password for
        new_password: New password to set
        current_admin: Current authenticated super admin
        db: Database session
    
    Returns:
        Success message
    
    Raises:
        HTTPException 400: Invalid admin ID or password
        HTTPException 404: Admin user not found
    """
    # Validate new password length
    if len(new_password) < 8:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail='New password must be at least 8 characters'
        )
    
    # Validate UUID
    try:
        target_admin_id = uuid.UUID(admin_id)
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail='Invalid admin ID format'
        )
    
    # Fetch target admin from database
    query = select(Admin).where(Admin.id == target_admin_id)
    result = await db.execute(query)
    admin = result.scalar_one_or_none()
    
    if not admin:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail='Admin user not found'
        )
    
    # Set new password
    admin.password_hash = hash_password(new_password)
    await db.commit()
    
    return {'message': 'Password reset successful for admin user'}


@admin_auth_router.get('/me')
async def get_current_admin_info(
    current_admin: dict = Depends(get_current_admin)
) -> dict:
    """
    Get current authenticated admin information.

    Args:
        current_admin: Current authenticated admin from JWT token

    Returns:
        Admin information (admin_id, email, role)
    """
    return current_admin
