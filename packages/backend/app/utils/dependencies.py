"""FastAPI dependencies for authentication and authorization."""
from fastapi import HTTPException, Request, status
from jose import JWTError, jwt

from app.config import get_settings


async def get_current_user(request: Request) -> dict:
    """
    Extract and validate JWT token from cookie.

    Args:
        request: FastAPI request object

    Returns:
        Dictionary with user_id and username claims

    Raises:
        HTTPException 401: Token missing, invalid, or expired
    """
    token = request.cookies.get('access_token')

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
        user_id: str | None = payload.get('user_id')
        username: str | None = payload.get('username')

        if user_id is None or username is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail='Invalid authentication credentials',
            )

        return {'user_id': user_id, 'username': username}

    except JWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail='Invalid authentication credentials',
        )
