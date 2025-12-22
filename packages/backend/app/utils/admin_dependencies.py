"""FastAPI dependencies for admin authentication and authorization."""
from uuid import UUID

from fastapi import HTTPException, Request, status
from jose import JWTError, jwt
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.config import get_settings
from app.database import get_db
from app.models.admin import Admin, AdminRole


async def get_current_admin(request: Request) -> dict:
    """
    Extract and validate admin JWT token from cookie.

    Args:
        request: FastAPI request object

    Returns:
        Dictionary with admin_id, email, and role claims

    Raises:
        HTTPException 401: Token missing, invalid, or expired
        HTTPException 403: Token is not an admin token
    """
    token = request.cookies.get('admin_token')

    if not token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail='Not authenticated',
            headers={'WWW-Authenticate': 'Bearer'},
        )

    settings = get_settings()

    try:
        payload = jwt.decode(
            token, settings.jwt_secret_key, algorithms=[settings.jwt_algorithm]
        )
        
        # Verify token type
        token_type: str | None = payload.get('type')
        if token_type != 'admin':
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail='Invalid token type - admin access required',
            )

        admin_id: str | None = payload.get('admin_id')
        email: str | None = payload.get('email')
        role: str | None = payload.get('role')

        if admin_id is None or email is None or role is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail='Invalid authentication credentials',
            )

        return {'admin_id': admin_id, 'email': email, 'role': role}

    except JWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail='Invalid authentication credentials',
        )


def require_admin_role(*allowed_roles: AdminRole):
    """
    Dependency factory to require specific admin roles.

    Args:
        *allowed_roles: One or more AdminRole values required

    Returns:
        Async dependency function that verifies admin has required role

    Usage:
        @router.get("/admin/users", dependencies=[Depends(require_admin_role(AdminRole.SUPER_ADMIN))])
    """
    async def role_checker(current_admin: dict = Depends(get_current_admin)) -> dict:
        admin_role = current_admin.get('role')
        
        # Convert string role to AdminRole enum for comparison
        try:
            current_role = AdminRole(admin_role)
        except ValueError:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail='Invalid admin role',
            )

        if current_role not in allowed_roles:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Requires one of roles: {', '.join(r.value for r in allowed_roles)}",
            )
        
        return current_admin

    return role_checker


# Import Depends here to avoid circular import
from fastapi import Depends  # noqa: E402
