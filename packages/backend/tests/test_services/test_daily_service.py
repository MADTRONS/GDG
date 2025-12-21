"""Tests for Daily.co service."""
import pytest
import responses
from app.services.daily_service import DailyService


class TestDailyService:
    """Test suite for DailyService."""
    
    @pytest.mark.asyncio
    @responses.activate
    async def test_create_room_success(self):
        """Test successful room creation."""
        service = DailyService()
        
        responses.add(
            responses.POST,
            "https://api.daily.co/v1/rooms",
            json={
                "url": "https://example.daily.co/test-room",
                "name": "test-room",
                "config": {"max_participants": 2}
            },
            status=200
        )
        
        result = await service.create_room("test-room")
        
        assert result["room_url"] == "https://example.daily.co/test-room"
        assert result["room_name"] == "test-room"
        assert result["config"]["max_participants"] == 2
    
    @pytest.mark.asyncio
    @responses.activate
    async def test_create_room_api_failure(self):
        """Test room creation with API failure."""
        service = DailyService()
        
        responses.add(
            responses.POST,
            "https://api.daily.co/v1/rooms",
            json={"error": "API error"},
            status=500
        )
        
        with pytest.raises(Exception, match="Failed to create Daily.co room"):
            await service.create_room("test-room")
    
    @pytest.mark.asyncio
    @responses.activate
    async def test_create_user_token_success(self):
        """Test successful user token creation."""
        service = DailyService()
        
        responses.add(
            responses.POST,
            "https://api.daily.co/v1/meeting-tokens",
            json={"token": "user-token-123"},
            status=200
        )
        
        token = await service.create_user_token("test-room", "user-id-456")
        
        assert token == "user-token-123"
    
    @pytest.mark.asyncio
    @responses.activate
    async def test_create_user_token_failure(self):
        """Test user token creation with API failure."""
        service = DailyService()
        
        responses.add(
            responses.POST,
            "https://api.daily.co/v1/meeting-tokens",
            json={"error": "Invalid room"},
            status=404
        )
        
        with pytest.raises(Exception, match="Failed to create user token"):
            await service.create_user_token("invalid-room", "user-id")
    
    @pytest.mark.asyncio
    @responses.activate
    async def test_create_bot_token_success(self):
        """Test successful bot token creation."""
        service = DailyService()
        
        responses.add(
            responses.POST,
            "https://api.daily.co/v1/meeting-tokens",
            json={"token": "bot-token-789"},
            status=200
        )
        
        token = await service.create_bot_token("test-room")
        
        assert token == "bot-token-789"
    
    @pytest.mark.asyncio
    @responses.activate
    async def test_create_bot_token_with_owner_permissions(self):
        """Test bot token has owner permissions."""
        service = DailyService()
        
        responses.add(
            responses.POST,
            "https://api.daily.co/v1/meeting-tokens",
            json={"token": "bot-token-owner"},
            status=200
        )
        
        token = await service.create_bot_token("test-room")
        
        assert token == "bot-token-owner"
        # Verify request payload (check last request)
        assert len(responses.calls) == 1
        request_body = responses.calls[0].request.body
        assert b'"is_owner": true' in request_body or b'"is_owner":true' in request_body
    
    @pytest.mark.asyncio
    @responses.activate
    async def test_delete_room_success(self):
        """Test successful room deletion."""
        service = DailyService()
        
        responses.add(
            responses.DELETE,
            "https://api.daily.co/v1/rooms/test-room",
            status=200
        )
        
        result = await service.delete_room("test-room")
        
        assert result is True
    
    @pytest.mark.asyncio
    @responses.activate
    async def test_delete_room_failure(self):
        """Test room deletion returns False on failure."""
        service = DailyService()
        
        responses.add(
            responses.DELETE,
            "https://api.daily.co/v1/rooms/test-room",
            status=404
        )
        
        result = await service.delete_room("test-room")
        
        assert result is False
