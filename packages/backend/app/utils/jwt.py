"""JWT token generation and validation utilities."""
import uuid
from datetime import UTC, datetime, timedelta

from jose import jwt

from app.config import get_settings


def create_access_token(user_id: uuid.UUID, username: str) -> str:
    \"\"\"
    Create JWT access token with user claims.

    Args:
        user_id: User's UUID
        username: User's username

    Returns:
        Encoded JWT token as string

    Example:
        >>> token = create_access_token(user_id=uuid4(), username='\\\\COLLEGE\\\\jdoe')
        >>> # Token can be decoded to verify claims
    \"\"\"
    settings = get_settings()

    # Calculate expiration time
    expire = datetime.now(UTC) + timedelta(minutes=settings.jwt_expiration_minutes)

    # Prepare claims
    to_encode = {
        'user_id': str(user_id),
        'username': username,
        'exp': expire,
        'iat': datetime.now(UTC),
    }

    # Encode token
    encoded_jwt = jwt.encode(
        to_encode,
        settings.jwt_secret_key,
        algorithm=settings.jwt_algorithm
    )

    return encoded_jwt
