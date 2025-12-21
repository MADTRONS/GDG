"""Tests for voice calling router."""
import pytest
from unittest.mock import Mock, AsyncMock, patch
from fastapi import HTTPException, status
from app.routers.voice import router, CreateRoomRequest


class TestVoiceRouter:
    """Test suite for voice calling endpoints."""
    
    @pytest.mark.asyncio
    async def test_create_room_success(self):
        """Test successful room creation flow."""
        # Mock dependencies
        mock_daily_service = Mock()
        mock_daily_service.create_room = AsyncMock(return_value={
            "room_url": "https://example.daily.co/test-room",
            "room_name": "test-room"
        })
        mock_daily_service.create_user_token = AsyncMock(return_value="user-token-123")
        mock_daily_service.create_bot_token = AsyncMock(return_value="bot-token-456")
        
        mock_pipecat_service = Mock()
        mock_pipecat_service.spawn_bot = AsyncMock(return_value=12345)
        
        mock_session_repo = Mock()
        mock_session_repo.create_session = AsyncMock(return_value=Mock(id="session-id-789"))
        
        mock_counselor_repo = Mock()
        mock_counselor = Mock()
        mock_counselor.id = "counselor-123"
        mock_counselor.category = "Health & Wellness"
        mock_counselor_repo.get_by_category = AsyncMock(return_value=mock_counselor)
        
        # Mock user
        mock_user = Mock()
        mock_user.id = "user-456"
        
        # Import and patch the endpoint function
        with patch('app.routers.voice.DailyService', return_value=mock_daily_service), \
             patch('app.routers.voice.PipeCatService', return_value=mock_pipecat_service), \
             patch('app.routers.voice.SessionRepository', return_value=mock_session_repo), \
             patch('app.routers.voice.CounselorRepository', return_value=mock_counselor_repo):
            
            from app.routers.voice import create_room
            
            request = CreateRoomRequest(counselor_category="Health & Wellness")
            response = await create_room(request, mock_user, Mock())
            
            assert response.room_url == "https://example.daily.co/test-room"
            assert response.user_token == "user-token-123"
            assert response.room_name == "test-room"
            assert response.session_id == "session-id-789"
            
            # Verify service calls
            mock_daily_service.create_room.assert_called_once()
            mock_daily_service.create_user_token.assert_called_once()
            mock_daily_service.create_bot_token.assert_called_once()
            mock_pipecat_service.spawn_bot.assert_called_once()
            mock_session_repo.create_session.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_create_room_invalid_category(self):
        """Test room creation with invalid counselor category."""
        mock_counselor_repo = Mock()
        mock_counselor_repo.get_by_category = AsyncMock(return_value=None)
        
        mock_user = Mock()
        mock_user.id = "user-456"
        
        with patch('app.routers.voice.CounselorRepository', return_value=mock_counselor_repo):
            from app.routers.voice import create_room
            
            request = CreateRoomRequest(counselor_category="Invalid Category")
            
            with pytest.raises(HTTPException) as exc_info:
                await create_room(request, mock_user, Mock())
            
            assert exc_info.value.status_code == status.HTTP_404_NOT_FOUND
            assert "No counselor found" in str(exc_info.value.detail)
    
    @pytest.mark.asyncio
    async def test_create_room_daily_api_failure(self):
        """Test room creation with Daily.co API failure."""
        mock_daily_service = Mock()
        mock_daily_service.create_room = AsyncMock(side_effect=Exception("Daily API error"))
        
        mock_counselor_repo = Mock()
        mock_counselor = Mock()
        mock_counselor.id = "counselor-123"
        mock_counselor.category = "Health & Wellness"
        mock_counselor_repo.get_by_category = AsyncMock(return_value=mock_counselor)
        
        mock_user = Mock()
        mock_user.id = "user-456"
        
        with patch('app.routers.voice.DailyService', return_value=mock_daily_service), \
             patch('app.routers.voice.CounselorRepository', return_value=mock_counselor_repo):
            
            from app.routers.voice import create_room
            
            request = CreateRoomRequest(counselor_category="Health & Wellness")
            
            with pytest.raises(HTTPException) as exc_info:
                await create_room(request, mock_user, Mock())
            
            assert exc_info.value.status_code == status.HTTP_500_INTERNAL_SERVER_ERROR
            assert "Failed to create voice room" in str(exc_info.value.detail)
    
    @pytest.mark.asyncio
    async def test_create_room_bot_spawn_failure(self):
        """Test room creation with bot spawn failure."""
        mock_daily_service = Mock()
        mock_daily_service.create_room = AsyncMock(return_value={
            "room_url": "https://example.daily.co/test-room",
            "room_name": "test-room"
        })
        mock_daily_service.create_user_token = AsyncMock(return_value="user-token")
        mock_daily_service.create_bot_token = AsyncMock(return_value="bot-token")
        mock_daily_service.delete_room = AsyncMock(return_value=True)
        
        mock_pipecat_service = Mock()
        mock_pipecat_service.spawn_bot = AsyncMock(side_effect=Exception("Bot spawn failed"))
        
        mock_counselor_repo = Mock()
        mock_counselor = Mock()
        mock_counselor.id = "counselor-123"
        mock_counselor.category = "Health & Wellness"
        mock_counselor_repo.get_by_category = AsyncMock(return_value=mock_counselor)
        
        mock_user = Mock()
        mock_user.id = "user-456"
        
        with patch('app.routers.voice.DailyService', return_value=mock_daily_service), \
             patch('app.routers.voice.PipeCatService', return_value=mock_pipecat_service), \
             patch('app.routers.voice.CounselorRepository', return_value=mock_counselor_repo):
            
            from app.routers.voice import create_room
            
            request = CreateRoomRequest(counselor_category="Health & Wellness")
            
            with pytest.raises(HTTPException) as exc_info:
                await create_room(request, mock_user, Mock())
            
            assert exc_info.value.status_code == status.HTTP_500_INTERNAL_SERVER_ERROR
            # Verify room cleanup was attempted
            mock_daily_service.delete_room.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_create_room_requires_authentication(self):
        """Test endpoint requires authentication."""
        # This test verifies the endpoint dependency
        from app.routers.voice import create_room
        import inspect
        
        sig = inspect.signature(create_room)
        params = sig.parameters
        
        # Verify current_user parameter exists
        assert 'current_user' in params
        
        # Verify it uses the authentication dependency
        param = params['current_user']
        assert param.default is not inspect.Parameter.empty
    
    @pytest.mark.asyncio
    async def test_create_room_generates_unique_session_id(self):
        """Test that each room creation generates unique session ID."""
        mock_daily_service = Mock()
        mock_daily_service.create_room = AsyncMock(return_value={
            "room_url": "https://example.daily.co/test",
            "room_name": "test"
        })
        mock_daily_service.create_user_token = AsyncMock(return_value="token1")
        mock_daily_service.create_bot_token = AsyncMock(return_value="token2")
        
        mock_pipecat_service = Mock()
        mock_pipecat_service.spawn_bot = AsyncMock(return_value=12345)
        
        session_ids = []
        def capture_session_id(*args, **kwargs):
            session_ids.append(kwargs.get('session_id') or args[0] if args else None)
            return AsyncMock(return_value=Mock(id=session_ids[-1]))()
        
        mock_session_repo = Mock()
        mock_session_repo.create_session = AsyncMock(side_effect=capture_session_id)
        
        mock_counselor_repo = Mock()
        mock_counselor = Mock()
        mock_counselor.id = "counselor-123"
        mock_counselor.category = "Health & Wellness"
        mock_counselor_repo.get_by_category = AsyncMock(return_value=mock_counselor)
        
        mock_user = Mock()
        mock_user.id = "user-456"
        
        with patch('app.routers.voice.DailyService', return_value=mock_daily_service), \
             patch('app.routers.voice.PipeCatService', return_value=mock_pipecat_service), \
             patch('app.routers.voice.SessionRepository', return_value=mock_session_repo), \
             patch('app.routers.voice.CounselorRepository', return_value=mock_counselor_repo):
            
            from app.routers.voice import create_room
            
            request = CreateRoomRequest(counselor_category="Health & Wellness")
            
            # Create two rooms
            await create_room(request, mock_user, Mock())
            await create_room(request, mock_user, Mock())
            
            # Verify different session IDs
            assert len(session_ids) == 2
            assert session_ids[0] != session_ids[1]
