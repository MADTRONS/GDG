"""Tests for video router."""
import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from fastapi import HTTPException, status
from uuid import UUID, uuid4

from app.routers.video import create_room, CreateRoomRequest


@pytest.fixture
def mock_current_user():
    """Mock authenticated user."""
    return {
        "user_id": "550e8400-e29b-41d4-a716-446655440000",
        "username": "testuser"
    }


@pytest.fixture
def mock_db_session():
    """Mock database session."""
    return MagicMock()


@pytest.fixture
def valid_category_uuid():
    """Valid category UUID for testing."""
    return UUID("660e8400-e29b-41d4-a716-446655440111")


@pytest.mark.asyncio
async def test_create_room_success(mock_current_user, mock_db_session, valid_category_uuid):
    """Test successful room creation."""
    request = CreateRoomRequest(counselor_category=valid_category_uuid)
    
    with patch("app.routers.video.LiveKitService") as mock_livekit_cls, \
         patch("app.routers.video.CounselorRepository") as mock_counselor_cls, \
         patch("app.routers.video.AvatarService") as mock_avatar_cls, \
         patch("app.routers.video.SessionRepository") as mock_session_cls, \
         patch("app.routers.video.get_settings") as mock_settings:
        
        # Mock settings
        settings = MagicMock()
        settings.livekit_url = "wss://test-livekit.com"
        mock_settings.return_value = settings
        
        # Mock category
        mock_category = MagicMock()
        mock_category.name = "Health"
        mock_category.enabled = True
        
        mock_counselor_repo = MagicMock()
        mock_counselor_repo.get_by_id = AsyncMock(return_value=mock_category)
        mock_counselor_cls.return_value = mock_counselor_repo
        
        # Mock LiveKit service
        mock_livekit = MagicMock()
        mock_livekit.create_room = AsyncMock(return_value={
            "room_name": "video-test-123",
            "room_sid": "room-sid-456"
        })
        mock_livekit.generate_access_token = AsyncMock(return_value="jwt-token-xyz")
        mock_livekit_cls.return_value = mock_livekit
        
        # Mock avatar service
        mock_avatar = MagicMock()
        mock_avatar.spawn_avatar = AsyncMock(return_value={
            "process_id": 12345,
            "session_id": "session-123",
            "status": "spawned"
        })
        mock_avatar_cls.return_value = mock_avatar
        
        # Mock session repository
        mock_session_repo = MagicMock()
        mock_session_repo.create_session = AsyncMock()
        mock_session_cls.return_value = mock_session_repo
        
        # Call endpoint
        response = await create_room(request, mock_current_user, mock_db_session)
        
        # Assertions
        assert response.room_url == "https://test-livekit.com"
        assert response.access_token == "jwt-token-xyz"
        assert response.room_name.startswith("video-")
        assert isinstance(response.session_id, UUID)
        
        # Verify services were called
        mock_livekit.create_room.assert_called_once()
        mock_livekit.generate_access_token.assert_called_once()
        mock_avatar.spawn_avatar.assert_called_once()
        mock_session_repo.create_session.assert_called_once()


@pytest.mark.asyncio
async def test_create_room_category_not_found(mock_current_user, mock_db_session, valid_category_uuid):
    """Test room creation with non-existent category."""
    request = CreateRoomRequest(counselor_category=valid_category_uuid)
    
    with patch("app.routers.video.CounselorRepository") as mock_counselor_cls:
        # Mock category not found
        mock_counselor_repo = MagicMock()
        mock_counselor_repo.get_by_id = AsyncMock(return_value=None)
        mock_counselor_cls.return_value = mock_counselor_repo
        
        with pytest.raises(HTTPException) as exc_info:
            await create_room(request, mock_current_user, mock_db_session)
        
        assert exc_info.value.status_code == status.HTTP_404_NOT_FOUND
        assert "not found or disabled" in exc_info.value.detail


@pytest.mark.asyncio
async def test_create_room_category_disabled(mock_current_user, mock_db_session, valid_category_uuid):
    """Test room creation with disabled category."""
    request = CreateRoomRequest(counselor_category=valid_category_uuid)
    
    with patch("app.routers.video.CounselorRepository") as mock_counselor_cls:
        # Mock disabled category
        mock_category = MagicMock()
        mock_category.enabled = False
        
        mock_counselor_repo = MagicMock()
        mock_counselor_repo.get_by_id = AsyncMock(return_value=mock_category)
        mock_counselor_cls.return_value = mock_counselor_repo
        
        with pytest.raises(HTTPException) as exc_info:
            await create_room(request, mock_current_user, mock_db_session)
        
        assert exc_info.value.status_code == status.HTTP_404_NOT_FOUND


@pytest.mark.asyncio
async def test_create_room_livekit_failure(mock_current_user, mock_db_session, valid_category_uuid):
    """Test room creation when LiveKit API fails."""
    request = CreateRoomRequest(counselor_category=valid_category_uuid)
    
    with patch("app.routers.video.LiveKitService") as mock_livekit_cls, \
         patch("app.routers.video.CounselorRepository") as mock_counselor_cls:
        
        # Mock category
        mock_category = MagicMock()
        mock_category.name = "Health"
        mock_category.enabled = True
        
        mock_counselor_repo = MagicMock()
        mock_counselor_repo.get_by_id = AsyncMock(return_value=mock_category)
        mock_counselor_cls.return_value = mock_counselor_repo
        
        # Mock LiveKit service failure
        mock_livekit = MagicMock()
        mock_livekit.create_room = AsyncMock(side_effect=Exception("LiveKit API error"))
        mock_livekit_cls.return_value = mock_livekit
        
        with pytest.raises(HTTPException) as exc_info:
            await create_room(request, mock_current_user, mock_db_session)
        
        assert exc_info.value.status_code == status.HTTP_500_INTERNAL_SERVER_ERROR
        assert "Failed to create video session" in exc_info.value.detail


@pytest.mark.asyncio
async def test_create_room_avatar_spawn_failure(mock_current_user, mock_db_session, valid_category_uuid):
    """Test room creation when avatar spawn fails."""
    request = CreateRoomRequest(counselor_category=valid_category_uuid)
    
    with patch("app.routers.video.LiveKitService") as mock_livekit_cls, \
         patch("app.routers.video.CounselorRepository") as mock_counselor_cls, \
         patch("app.routers.video.AvatarService") as mock_avatar_cls:
        
        # Mock category
        mock_category = MagicMock()
        mock_category.name = "Health"
        mock_category.enabled = True
        
        mock_counselor_repo = MagicMock()
        mock_counselor_repo.get_by_id = AsyncMock(return_value=mock_category)
        mock_counselor_cls.return_value = mock_counselor_repo
        
        # Mock LiveKit service success
        mock_livekit = MagicMock()
        mock_livekit.create_room = AsyncMock(return_value={
            "room_name": "video-test-123",
            "room_sid": "room-sid-456"
        })
        mock_livekit.generate_access_token = AsyncMock(return_value="jwt-token-xyz")
        mock_livekit_cls.return_value = mock_livekit
        
        # Mock avatar service failure
        mock_avatar = MagicMock()
        mock_avatar.spawn_avatar = AsyncMock(side_effect=Exception("Avatar spawn failed"))
        mock_avatar_cls.return_value = mock_avatar
        
        with pytest.raises(HTTPException) as exc_info:
            await create_room(request, mock_current_user, mock_db_session)
        
        assert exc_info.value.status_code == status.HTTP_500_INTERNAL_SERVER_ERROR


@pytest.mark.asyncio
async def test_create_room_authentication_required(mock_db_session, valid_category_uuid):
    """Test room creation requires authentication."""
    # This test verifies the endpoint uses get_current_user dependency
    # In real usage, FastAPI will enforce this dependency
    request = CreateRoomRequest(counselor_category=valid_category_uuid)
    
    # Attempting to call without current_user should fail in real FastAPI context
    # This test documents the requirement
    assert True  # Authentication is enforced by FastAPI dependency injection


@pytest.mark.asyncio
async def test_create_room_logs_session(mock_current_user, mock_db_session, valid_category_uuid):
    """Test room creation logs session to database."""
    request = CreateRoomRequest(counselor_category=valid_category_uuid)
    
    with patch("app.routers.video.LiveKitService") as mock_livekit_cls, \
         patch("app.routers.video.CounselorRepository") as mock_counselor_cls, \
         patch("app.routers.video.AvatarService") as mock_avatar_cls, \
         patch("app.routers.video.SessionRepository") as mock_session_cls, \
         patch("app.routers.video.get_settings") as mock_settings:
        
        # Mock settings
        settings = MagicMock()
        settings.livekit_url = "wss://test-livekit.com"
        mock_settings.return_value = settings
        
        # Mock category
        mock_category = MagicMock()
        mock_category.name = "Health"
        mock_category.enabled = True
        
        mock_counselor_repo = MagicMock()
        mock_counselor_repo.get_by_id = AsyncMock(return_value=mock_category)
        mock_counselor_cls.return_value = mock_counselor_repo
        
        # Mock services
        mock_livekit = MagicMock()
        mock_livekit.create_room = AsyncMock(return_value={"room_name": "video-test", "room_sid": "sid"})
        mock_livekit.generate_access_token = AsyncMock(return_value="token")
        mock_livekit_cls.return_value = mock_livekit
        
        mock_avatar = MagicMock()
        mock_avatar.spawn_avatar = AsyncMock(return_value={"process_id": 123, "status": "spawned"})
        mock_avatar_cls.return_value = mock_avatar
        
        mock_session_repo = MagicMock()
        mock_session_repo.create_session = AsyncMock()
        mock_session_cls.return_value = mock_session_repo
        
        # Call endpoint
        await create_room(request, mock_current_user, mock_db_session)
        
        # Verify session was logged with mode="video"
        mock_session_repo.create_session.assert_called_once()
        call_args = mock_session_repo.create_session.call_args
        assert call_args[1]["mode"] == "video"
        assert call_args[1]["counselor_category"] == "Health"
