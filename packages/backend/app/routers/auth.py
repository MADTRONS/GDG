"""Authentication router for login/logout endpoints."""
from fastapi import APIRouter, Depends, HTTPException, Response, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.repositories.user_repository import UserRepository
from app.schemas.auth import LoginRequest, LoginResponse
from app.schemas.user import UserResponse
from app.utils.jwt import create_access_token
from app.utils.security import verify_password

auth_router = APIRouter(prefix='/api/auth', tags=['authentication'])


async def get_user_repository(session: AsyncSession = Depends(get_db)) -> UserRepository:
    """Dependency to get user repository instance."""
    return UserRepository(session)


@auth_router.post('/login', response_model=LoginResponse)
async def login(
    credentials: LoginRequest,
    response: Response,
    user_repo: UserRepository = Depends(get_user_repository)
) -> LoginResponse:
    """
    Authenticate user and return JWT token.

    Args:
        credentials: Login credentials (username and password)
        response: FastAPI response object for setting cookies
        user_repo: User repository for database queries

    Returns:
        LoginResponse with access token and user data

    Raises:
        HTTPException 401: Invalid credentials or user not found
        HTTPException 403: User account is blocked
    """
    # Query database for user
    user = await user_repo.get_by_username(credentials.username)

    # Check if user exists
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail='Invalid username or password'
        )

    # Check if user is blocked
    if user.is_blocked:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail='Your account has been blocked. Please reach out to support for help.'
        )

    # Verify password
    if not verify_password(credentials.password, user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail='Invalid username or password'
        )

    # Generate JWT token
    access_token = create_access_token(user_id=user.id, username=user.username)

    # Set httpOnly cookie
    response.set_cookie(
        key='access_token',
        value=access_token,
        httponly=True,
        secure=True,
        samesite='lax',
        max_age=86400
    )

    # Return response
    return LoginResponse(
        access_token=access_token,
        token_type='bearer',
        user=UserResponse.model_validate(user)
    )