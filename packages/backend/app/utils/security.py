"""Security utilities for password hashing and verification."""
import bcrypt


def hash_password(password: str) -> str:
    \"\"\"
    Hash a password using bcrypt with work factor 12.

    Args:
        password: Plain text password to hash

    Returns:
        Hashed password as string

    Example:
        >>> hashed = hash_password('mypassword')
        >>> verify_password('mypassword', hashed)
        True
    \"\"\"
    password_bytes = password.encode('utf-8')
    salt = bcrypt.gensalt(rounds=12)
    hashed = bcrypt.hashpw(password_bytes, salt)
    return hashed.decode('utf-8')


def verify_password(plain_password: str, hashed_password: str) -> bool:
    \"\"\"
    Verify a password against its hash using timing-safe comparison.

    Args:
        plain_password: Plain text password to verify
        hashed_password: Hashed password to compare against

    Returns:
        True if password matches, False otherwise

    Example:
        >>> hashed = hash_password('mypassword')
        >>> verify_password('mypassword', hashed)
        True
        >>> verify_password('wrongpassword', hashed)
        False
    \"\"\"
    password_bytes = plain_password.encode('utf-8')
    hashed_bytes = hashed_password.encode('utf-8')
    return bcrypt.checkpw(password_bytes, hashed_bytes)
