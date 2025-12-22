"""Admin authentication router for login/logout endpoints."""
from datetime import UTC, datetime
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Response, status
from pydantic import BaseModel, EmailStr
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.config import get_settings
from app.database import get_db
from app.models.admin import Admin
from app.utils.admin_dependencies import get_current_admin
from app.utils.admin_jwt import create_admin_access_token
from app.utils.security import verify_password

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
