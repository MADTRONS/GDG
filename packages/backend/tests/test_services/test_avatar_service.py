"""Tests for Avatar service."""
import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from uuid import UUID

from app.services.avatar_service import AvatarService


@pytest.fixture
def mock_counselor_repo():
    """Mock counselor repository."""
    repo = MagicMock()
    return repo


@pytest.fixture
def mock_settings():
    """Mock settings for testing."""
    with patch("app.services.avatar_service.get_settings") as mock:
        settings = MagicMock()
        settings.livekit_url = "wss://test-livekit-server.com"
        settings.livekit_api_key = "test-api-key"
        settings.livekit_api_secret = "test-api-secret"
        settings.bey_avatar_id = "avatar-123"
        settings.openai_api_key = "openai-key-456"
        mock.return_value = settings
        yield settings


@pytest.mark.asyncio
async def test_spawn_avatar_success(mock_counselor_repo, mock_settings):
    """Test successful avatar spawn."""
    service = AvatarService(mock_counselor_repo)
    
    # Mock category
    mock_category = MagicMock()
    mock_category.name = "Health"
    mock_category.system_prompt = "You are a health counselor."
    mock_counselor_repo.get_by_id = AsyncMock(return_value=mock_category)
    
    with patch("app.services.avatar_service.subprocess.Popen") as mock_popen:
        mock_process = MagicMock()
        mock_process.pid = 12345
        mock_popen.return_value = mock_process
        
        result = await service.spawn_avatar(
            room_name="test-room",
            session_id="session-123",
            category_id="550e8400-e29b-41d4-a716-446655440000"
        )
        
        # Assertions
        assert result["process_id"] == 12345
        assert result["session_id"] == "session-123"
        assert result["status"] == "spawned"
        
        # Verify counselor repo was called
        mock_counselor_repo.get_by_id.assert_called_once()
        
        # Verify subprocess.Popen was called with correct environment
        mock_popen.assert_called_once()
        call_kwargs = mock_popen.call_args[1]
        env = call_kwargs["env"]
        
        assert env["LIVEKIT_URL"] == "wss://test-livekit-server.com"
        assert env["LIVEKIT_API_KEY"] == "test-api-key"
        assert env["ROOM_NAME"] == "test-room"
        assert env["SESSION_ID"] == "session-123"
        assert env["AVATAR_ID"] == "avatar-123"
        assert env["OPENAI_API_KEY"] == "openai-key-456"
        assert env["SYSTEM_PROMPT"] == "You are a health counselor."
        assert env["COUNSELOR_CATEGORY"] == "Health"


@pytest.mark.asyncio
async def test_spawn_avatar_invalid_category(mock_counselor_repo, mock_settings):
    """Test avatar spawn with invalid category."""
    service = AvatarService(mock_counselor_repo)
    
    # Mock category not found
    mock_counselor_repo.get_by_id = AsyncMock(return_value=None)
    
    with pytest.raises(ValueError) as exc_info:
        await service.spawn_avatar(
            room_name="test-room",
            session_id="session-123",
            category_id="550e8400-e29b-41d4-a716-446655440000"  # Valid UUID format
        )
    
    assert "Invalid counselor category" in str(exc_info.value)


@pytest.mark.asyncio
async def test_spawn_avatar_no_system_prompt(mock_counselor_repo, mock_settings):
    """Test avatar spawn uses default prompt if category has none."""
    service = AvatarService(mock_counselor_repo)
    
    # Mock category without system prompt
    mock_category = MagicMock()
    mock_category.name = "Career"
    mock_category.system_prompt = None  # No custom prompt
    mock_counselor_repo.get_by_id = AsyncMock(return_value=mock_category)
    
    with patch("app.services.avatar_service.subprocess.Popen") as mock_popen:
        mock_process = MagicMock()
        mock_process.pid = 12345
        mock_popen.return_value = mock_process
        
        result = await service.spawn_avatar(
            room_name="test-room",
            session_id="session-123",
            category_id="550e8400-e29b-41d4-a716-446655440000"
        )
        
        # Verify default prompt was used
        call_kwargs = mock_popen.call_args[1]
        env = call_kwargs["env"]
        assert "supportive counselor" in env["SYSTEM_PROMPT"]
        assert "empathetic" in env["SYSTEM_PROMPT"]


@pytest.mark.asyncio
async def test_spawn_avatar_subprocess_failure(mock_counselor_repo, mock_settings):
    """Test avatar spawn handles subprocess errors."""
    service = AvatarService(mock_counselor_repo)
    
    mock_category = MagicMock()
    mock_category.name = "Health"
    mock_category.system_prompt = "Test prompt"
    mock_counselor_repo.get_by_id = AsyncMock(return_value=mock_category)
    
    with patch("app.services.avatar_service.subprocess.Popen") as mock_popen:
        mock_popen.side_effect = Exception("Subprocess failed")
        
        with pytest.raises(Exception) as exc_info:
            await service.spawn_avatar(
                room_name="test-room",
                session_id="session-123",
                category_id="550e8400-e29b-41d4-a716-446655440000"
            )
        
        assert "Failed to spawn avatar agent" in str(exc_info.value)
        assert "Subprocess failed" in str(exc_info.value)


def test_get_default_prompt(mock_counselor_repo):
    """Test default prompt content."""
    service = AvatarService(mock_counselor_repo)
    
    default_prompt = service._get_default_prompt()
    
    # Verify default prompt has expected content
    assert "supportive counselor" in default_prompt
    assert "college students" in default_prompt
    assert "empathetic" in default_prompt
    assert "professional" in default_prompt
