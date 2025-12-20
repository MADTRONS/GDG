"""Tests for authentication dependencies."""
import uuid
from datetime import UTC, datetime, timedelta
from unittest.mock import MagicMock

import pytest
from fastapi import HTTPException
from jose import jwt

from app.config import get_settings
from app.utils.dependencies import get_current_user


@pytest.mark.asyncio
async def test_get_current_user_valid_token():
    """Test successful user extraction from valid token."""
    settings = get_settings()
    user_id = str(uuid.uuid4())
    username = r'\COLLEGE\testuser'

    # Create valid token
    payload = {
        'user_id': user_id,
        'username': username,
        'exp': datetime.now(UTC) + timedelta(hours=1),
        'iat': datetime.now(UTC),
    }
    token = jwt.encode(payload, settings.jwt_secret_key, algorithm=settings.jwt_algorithm)

    # Mock request with token in cookies
    mock_request = MagicMock()
    mock_request.cookies.get.return_value = token

    # Call function
    result = await get_current_user(mock_request)

    # Verify result
    assert result['user_id'] == user_id
    assert result['username'] == username


@pytest.mark.asyncio
async def test_get_current_user_missing_token():
    """Test raises 401 when no token present."""
    # Mock request without token
    mock_request = MagicMock()
    mock_request.cookies.get.return_value = None

    # Should raise 401
    with pytest.raises(HTTPException) as exc_info:
        await get_current_user(mock_request)

    assert exc_info.value.status_code == 401
    assert exc_info.value.detail == 'Not authenticated'


@pytest.mark.asyncio
async def test_get_current_user_invalid_token():
    """Test raises 401 when token is malformed."""
    # Mock request with invalid token
    mock_request = MagicMock()
    mock_request.cookies.get.return_value = 'invalid.token.here'

    # Should raise 401
    with pytest.raises(HTTPException) as exc_info:
        await get_current_user(mock_request)

    assert exc_info.value.status_code == 401
    assert exc_info.value.detail == 'Invalid authentication credentials'


@pytest.mark.asyncio
async def test_get_current_user_expired_token():
    """Test raises 401 when token is expired."""
    settings = get_settings()
    user_id = str(uuid.uuid4())
    username = r'\COLLEGE\testuser'

    # Create expired token
    payload = {
        'user_id': user_id,
        'username': username,
        'exp': datetime.now(UTC) - timedelta(hours=1),  # Expired 1 hour ago
        'iat': datetime.now(UTC) - timedelta(hours=2),
    }
    token = jwt.encode(payload, settings.jwt_secret_key, algorithm=settings.jwt_algorithm)

    # Mock request with expired token
    mock_request = MagicMock()
    mock_request.cookies.get.return_value = token

    # Should raise 401
    with pytest.raises(HTTPException) as exc_info:
        await get_current_user(mock_request)

    assert exc_info.value.status_code == 401
    assert exc_info.value.detail == 'Invalid authentication credentials'


@pytest.mark.asyncio
async def test_get_current_user_missing_user_id():
    """Test raises 401 when token missing user_id claim."""
    settings = get_settings()
    username = r'\COLLEGE\testuser'

    # Create token without user_id
    payload = {
        'username': username,
        'exp': datetime.now(UTC) + timedelta(hours=1),
        'iat': datetime.now(UTC),
    }
    token = jwt.encode(payload, settings.jwt_secret_key, algorithm=settings.jwt_algorithm)

    # Mock request
    mock_request = MagicMock()
    mock_request.cookies.get.return_value = token

    # Should raise 401
    with pytest.raises(HTTPException) as exc_info:
        await get_current_user(mock_request)

    assert exc_info.value.status_code == 401
    assert exc_info.value.detail == 'Invalid authentication credentials'


@pytest.mark.asyncio
async def test_get_current_user_missing_username():
    """Test raises 401 when token missing username claim."""
    settings = get_settings()
    user_id = str(uuid.uuid4())

    # Create token without username
    payload = {
        'user_id': user_id,
        'exp': datetime.now(UTC) + timedelta(hours=1),
        'iat': datetime.now(UTC),
    }
    token = jwt.encode(payload, settings.jwt_secret_key, algorithm=settings.jwt_algorithm)

    # Mock request
    mock_request = MagicMock()
    mock_request.cookies.get.return_value = token

    # Should raise 401
    with pytest.raises(HTTPException) as exc_info:
        await get_current_user(mock_request)

    assert exc_info.value.status_code == 401
    assert exc_info.value.detail == 'Invalid authentication credentials'
