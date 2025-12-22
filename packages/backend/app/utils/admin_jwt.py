"""JWT token generation utilities for admin authentication."""
import uuid
from datetime import UTC, datetime, timedelta

from jose import jwt

from app.config import get_settings


def create_admin_access_token(admin_id: uuid.UUID, email: str, role: str) -> str:
    """
    Create JWT access token with admin claims.

    Args:
        admin_id: Admin's UUID
        email: Admin's email address
        role: Admin's role (SUPER_ADMIN, SYSTEM_MONITOR, CONTENT_MANAGER)

    Returns:
        Encoded JWT token as string
    """
    settings = get_settings()

    # Calculate expiration time (8 hours for admin tokens)
    expire = datetime.now(UTC) + timedelta(hours=8)

    # Prepare claims
    to_encode = {
        'admin_id': str(admin_id),
        'email': email,
        'role': role,
        'type': 'admin',  # Distinguish from student tokens
        'exp': expire,
        'iat': datetime.now(UTC),
    }

    # Encode token (using same secret key as student tokens, but with 'type': 'admin')
    encoded_jwt = jwt.encode(
        to_encode,
        settings.jwt_secret_key,
        algorithm=settings.jwt_algorithm
    )

    return encoded_jwt
