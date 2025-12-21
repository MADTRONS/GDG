"""Tests for PipeCat service."""
import pytest
from unittest.mock import Mock, patch, MagicMock, AsyncMock
from app.services.pipecat_service import PipeCatService


class TestPipeCatService:
    """Test suite for PipeCatService."""
    
    @pytest.mark.asyncio
    @patch('app.services.pipecat_service.subprocess.Popen')
    async def test_spawn_bot_success(self, mock_popen):
        """Test successful bot spawning."""
        # Mock the subprocess
        mock_process = MagicMock()
        mock_process.pid = 12345
        mock_popen.return_value = mock_process
        
        # Mock counselor repository
        mock_counselor_repo = Mock()
        mock_counselor = Mock()
        mock_counselor.category = "Health & Wellness"
        mock_counselor_repo.get_by_id = AsyncMock(return_value=mock_counselor)
        
        service = PipeCatService(counselor_repo=mock_counselor_repo)
        
        result = await service.spawn_bot(
            room_url="https://example.daily.co/test-room",
            bot_token="bot-token-123",
            session_id="session-123",
            category_id="counselor-123"
        )
        
        assert result["bot_pid"] == 12345
        mock_popen.assert_called_once()
        
        # Verify environment variables were set
        call_kwargs = mock_popen.call_args[1]
        env = call_kwargs['env']
        assert 'DAILY_ROOM_URL' in env
        assert env['DAILY_ROOM_URL'] == "https://example.daily.co/test-room"
        assert 'DAILY_BOT_TOKEN' in env
        assert env['DAILY_BOT_TOKEN'] == "bot-token-123"
        assert 'DEEPGRAM_API_KEY' in env
        assert 'CARTESIA_API_KEY' in env
        assert 'GOOGLE_API_KEY' in env
    
    @pytest.mark.asyncio
    async def test_spawn_bot_invalid_category(self):
        """Test bot spawning with invalid counselor category."""
        # Mock counselor repository with None result
        mock_counselor_repo = Mock()
        mock_counselor_repo.get_by_id = AsyncMock(return_value=None)
        
        service = PipeCatService(counselor_repo=mock_counselor_repo)
        
        with pytest.raises(ValueError, match="Counselor not found"):
            await service.spawn_bot(
                room_url="https://example.daily.co/test-room",
                bot_token="bot-token-123",
                session_id="session-123",
                category_id="invalid-id"
            )
    
    @pytest.mark.asyncio
    @patch('app.services.pipecat_service.subprocess.Popen')
    async def test_spawn_bot_with_health_wellness_prompt(self, mock_popen):
        """Test bot uses correct prompt for Health & Wellness."""
        mock_process = MagicMock()
        mock_process.pid = 12345
        mock_popen.return_value = mock_process
        
        mock_counselor_repo = Mock()
        mock_counselor = Mock()
        mock_counselor.category = "Health & Wellness"
        mock_counselor_repo.get_by_id = AsyncMock(return_value=mock_counselor)
        
        service = PipeCatService(counselor_repo=mock_counselor_repo)
        
        await service.spawn_bot(
            room_url="https://example.daily.co/test",
            bot_token="token",
            session_id="session-123",
            category_id="123"
        )
        
        # Verify system prompt is set in environment
        call_kwargs = mock_popen.call_args[1]
        env = call_kwargs['env']
        assert 'SYSTEM_PROMPT' in env
        assert 'health' in env['SYSTEM_PROMPT'].lower()
    
    @pytest.mark.asyncio
    @patch('app.services.pipecat_service.subprocess.Popen')
    async def test_spawn_bot_with_academic_support_prompt(self, mock_popen):
        """Test bot uses correct prompt for Academic Support."""
        mock_process = MagicMock()
        mock_process.pid = 12345
        mock_popen.return_value = mock_process
        
        mock_counselor_repo = Mock()
        mock_counselor = Mock()
        mock_counselor.category = "Academic Support"
        mock_counselor_repo.get_by_id = AsyncMock(return_value=mock_counselor)
        
        service = PipeCatService(counselor_repo=mock_counselor_repo)
        
        await service.spawn_bot(
            room_url="https://example.daily.co/test",
            bot_token="token",
            session_id="session-456",
            category_id="456"
        )
        
        call_kwargs = mock_popen.call_args[1]
        env = call_kwargs['env']
        assert 'SYSTEM_PROMPT' in env
        assert 'academic' in env['SYSTEM_PROMPT'].lower()
    
    @pytest.mark.asyncio
    @patch('app.services.pipecat_service.subprocess.Popen')
    async def test_spawn_bot_subprocess_failure(self, mock_popen):
        """Test bot spawning handles subprocess failure."""
        mock_popen.side_effect = Exception("Failed to spawn process")
        
        mock_counselor_repo = Mock()
        mock_counselor = Mock()
        mock_counselor.category = "Health & Wellness"
        mock_counselor_repo.get_by_id = AsyncMock(return_value=mock_counselor)
        
        service = PipeCatService(counselor_repo=mock_counselor_repo)
        
        with pytest.raises(Exception, match="Failed to spawn process"):
            await service.spawn_bot(
                room_url="https://example.daily.co/test",
                bot_token="token",
                session_id="session-123",
                category_id="123"
            )
