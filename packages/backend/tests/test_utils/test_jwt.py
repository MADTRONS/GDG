"""Tests for JWT token generation and validation."""
import uuid
from datetime import UTC, datetime, timedelta

import pytest
from jose import jwt

from app.config import get_settings
from app.utils.jwt import create_access_token


def test_create_access_token():
    """Test JWT token generation with correct claims."""
    settings = get_settings()
    user_id = uuid.uuid4()
    username = r'\COLLEGE\testuser'
    
    # Create token
    token = create_access_token(user_id=user_id, username=username)
    
    # Token should be a string
    assert isinstance(token, str)
    assert len(token) > 0
    
    # Decode and verify claims
    decoded = jwt.decode(
        token,
        settings.jwt_secret_key,
        algorithms=[settings.jwt_algorithm]
    )
    
    assert decoded['user_id'] == str(user_id)
    assert decoded['username'] == username
    assert 'exp' in decoded
    assert 'iat' in decoded


def test_token_expiration():
    """Test token expires after configured time (24 hours)."""
    settings = get_settings()
    user_id = uuid.uuid4()
    username = r'\COLLEGE\testuser'
    
    # Create token
    token = create_access_token(user_id=user_id, username=username)
    
    # Decode token
    decoded = jwt.decode(
        token,
        settings.jwt_secret_key,
        algorithms=[settings.jwt_algorithm]
    )
    
    # Check expiration is approximately 24 hours from now
    exp_time = datetime.fromtimestamp(decoded['exp'], UTC)
    expected_exp = datetime.now(UTC) + timedelta(minutes=settings.jwt_expiration_minutes)
    
    # Allow 5 second tolerance for test execution time
    time_diff = abs((exp_time - expected_exp).total_seconds())
    assert time_diff < 5


def test_token_decode():
    """Test token can be decoded correctly."""
    settings = get_settings()
    user_id = uuid.uuid4()
    username = r'\COLLEGE\jdoe'
    
    # Create and decode
    token = create_access_token(user_id=user_id, username=username)
    decoded = jwt.decode(
        token,
        settings.jwt_secret_key,
        algorithms=[settings.jwt_algorithm]
    )
    
    # Verify all expected fields present
    assert 'user_id' in decoded
    assert 'username' in decoded
    assert 'exp' in decoded
    assert 'iat' in decoded


def test_token_different_users():
    """Test tokens are different for different users."""
    user_id1 = uuid.uuid4()
    user_id2 = uuid.uuid4()
    
    token1 = create_access_token(user_id=user_id1, username=r'\COLLEGE\user1')
    token2 = create_access_token(user_id=user_id2, username=r'\COLLEGE\user2')
    
    # Tokens should be different
    assert token1 != token2


def test_token_includes_issued_at():
    """Test token includes issued at (iat) claim."""
    settings = get_settings()
    user_id = uuid.uuid4()
    username = r'\COLLEGE\testuser'
    
    before = datetime.now(UTC)
    token = create_access_token(user_id=user_id, username=username)
    after = datetime.now(UTC)
    
    decoded = jwt.decode(
        token,
        settings.jwt_secret_key,
        algorithms=[settings.jwt_algorithm]
    )
    
    iat_time = datetime.fromtimestamp(decoded['iat'], UTC)
    
    # iat should be between before and after (with microsecond tolerance)
    # Strip microseconds for comparison
    before_no_micro = before.replace(microsecond=0)
    after_no_micro = after.replace(microsecond=0)
    iat_no_micro = iat_time.replace(microsecond=0)
    
    assert before_no_micro <= iat_no_micro <= after_no_micro