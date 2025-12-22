"""Tests for LiveKit service."""
import pytest
from unittest.mock import AsyncMock, MagicMock, patch

from app.services.livekit_service import LiveKitService


@pytest.fixture
def mock_settings():
    """Mock settings for testing."""
    with patch("app.services.livekit_service.get_settings") as mock:
        settings = MagicMock()
        settings.livekit_url = "wss://test-livekit-server.com"
        settings.livekit_api_key = "test-api-key"
        settings.livekit_api_secret = "test-api-secret"
        mock.return_value = settings
        yield settings


@pytest.mark.asyncio
async def test_create_room_success(mock_settings):
    """Test successful LiveKit room creation."""
    service = LiveKitService()
    
    with patch("app.services.livekit_service.api.LiveKitAPI") as mock_api_class:
        # Mock the API instance and room creation
        mock_api_instance = MagicMock()
        mock_api_class.return_value = mock_api_instance
        
        mock_room = MagicMock()
        mock_room.name = "test-room-123"
        mock_room.sid = "room-sid-456"
        
        mock_api_instance.room.create_room = AsyncMock(return_value=mock_room)
        
        # Call service
        result = await service.create_room("test-room-123")
        
        # Assertions
        assert result["room_name"] == "test-room-123"
        assert result["room_sid"] == "room-sid-456"
        
        # Verify API was called with correct parameters
        mock_api_instance.room.create_room.assert_called_once()
        call_args = mock_api_instance.room.create_room.call_args[0][0]
        assert call_args.name == "test-room-123"
        assert call_args.empty_timeout == 300
        assert call_args.max_participants == 2


@pytest.mark.asyncio
async def test_create_room_failure(mock_settings):
    """Test LiveKit room creation failure handling."""
    service = LiveKitService()
    
    with patch("app.services.livekit_service.api.LiveKitAPI") as mock_api_class:
        mock_api_instance = MagicMock()
        mock_api_class.return_value = mock_api_instance
        
        # Simulate API failure
        mock_api_instance.room.create_room = AsyncMock(
            side_effect=Exception("LiveKit API error")
        )
        
        # Should raise exception with helpful message
        with pytest.raises(Exception) as exc_info:
            await service.create_room("test-room")
        
        assert "Failed to create LiveKit room" in str(exc_info.value)
        assert "LiveKit API error" in str(exc_info.value)


@pytest.mark.asyncio
async def test_generate_access_token_success(mock_settings):
    """Test successful access token generation."""
    service = LiveKitService()
    
    with patch("app.services.livekit_service.api.AccessToken") as mock_token_class:
        mock_token = MagicMock()
        mock_token.to_jwt.return_value = "jwt-token-xyz"
        mock_token_class.return_value = mock_token
        
        # Call service
        token = await service.generate_access_token(
            room_name="test-room",
            participant_identity="user-123",
            participant_name="Test User"
        )
        
        # Assertions
        assert token == "jwt-token-xyz"
        
        # Verify token configuration
        mock_token.with_identity.assert_called_once_with("user-123")
        mock_token.with_name.assert_called_once_with("Test User")
        mock_token.with_ttl.assert_called_once()
        mock_token.with_grants.assert_called_once()
        
        # Verify grants
        grants_call = mock_token.with_grants.call_args[0][0]
        assert grants_call.room_join is True
        assert grants_call.room == "test-room"
        assert grants_call.can_publish is True
        assert grants_call.can_publish_data is True
        assert grants_call.can_subscribe is True


@pytest.mark.asyncio
async def test_generate_access_token_failure(mock_settings):
    """Test access token generation failure handling."""
    service = LiveKitService()
    
    with patch("app.services.livekit_service.api.AccessToken") as mock_token_class:
        # Simulate token generation failure
        mock_token_class.side_effect = Exception("Token generation failed")
        
        with pytest.raises(Exception) as exc_info:
            await service.generate_access_token(
                room_name="test-room",
                participant_identity="user-123",
                participant_name="Test User"
            )
        
        assert "Failed to generate access token" in str(exc_info.value)


@pytest.mark.asyncio
async def test_delete_room_success(mock_settings):
    """Test successful room deletion."""
    service = LiveKitService()
    
    with patch("app.services.livekit_service.api.LiveKitAPI") as mock_api_class:
        mock_api_instance = MagicMock()
        mock_api_class.return_value = mock_api_instance
        mock_api_instance.room.delete_room = AsyncMock()
        
        result = await service.delete_room("test-room")
        
        assert result is True
        mock_api_instance.room.delete_room.assert_called_once()


@pytest.mark.asyncio
async def test_delete_room_failure(mock_settings):
    """Test room deletion failure returns False."""
    service = LiveKitService()
    
    with patch("app.services.livekit_service.api.LiveKitAPI") as mock_api_class:
        mock_api_instance = MagicMock()
        mock_api_class.return_value = mock_api_instance
        mock_api_instance.room.delete_room = AsyncMock(
            side_effect=Exception("Delete failed")
        )
        
        result = await service.delete_room("test-room")
        
        assert result is False
