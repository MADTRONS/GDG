"""Service for interacting with LiveKit API."""
from datetime import timedelta
from typing import Dict

from livekit import api

from app.config import get_settings


class LiveKitService:
    """Service for creating LiveKit rooms and managing access tokens."""
    
    def __init__(self):
        """Initialize LiveKit service with configuration from settings."""
        settings = get_settings()
        self.api_key = settings.livekit_api_key
        self.api_secret = settings.livekit_api_secret
        self.livekit_url = settings.livekit_url  # e.g., wss://your-livekit-server.com
    
    async def create_room(self, room_name: str) -> Dict[str, str]:
        """
        Create a LiveKit room for video calling.
        
        Args:
            room_name: Unique identifier for the room
            
        Returns:
            Dict with room_name and room_sid
            
        Raises:
            Exception: If room creation fails
        """
        try:
            # Initialize LiveKit API client
            livekit_api = api.LiveKitAPI(
                url=self.livekit_url,
                api_key=self.api_key,
                api_secret=self.api_secret
            )
            
            # Create room with video enabled
            room = await livekit_api.room.create_room(
                api.CreateRoomRequest(
                    name=room_name,
                    empty_timeout=300,  # Room deleted after 5 min if empty
                    max_participants=2,  # Student + Avatar
                )
            )
            
            return {
                "room_name": room.name,
                "room_sid": room.sid,
            }
            
        except Exception as e:
            raise Exception(f"Failed to create LiveKit room: {str(e)}")
    
    async def generate_access_token(
        self,
        room_name: str,
        participant_identity: str,
        participant_name: str
    ) -> str:
        """
        Generate a LiveKit access token for a participant.
        
        Args:
            room_name: Name of the LiveKit room
            participant_identity: Unique identifier for participant
            participant_name: Display name for participant
            
        Returns:
            JWT access token string
            
        Raises:
            Exception: If token generation fails
        """
        try:
            token = api.AccessToken(
                api_key=self.api_key,
                api_secret=self.api_secret
            )
            
            # Set token identity and validity
            token.with_identity(participant_identity)
            token.with_name(participant_name)
            token.with_ttl(timedelta(hours=24))
            
            # Grant permissions for student participant
            token.with_grants(
                api.VideoGrants(
                    room_join=True,
                    room=room_name,
                    can_publish=True,  # Can publish audio
                    can_publish_data=True,
                    can_subscribe=True,  # Can subscribe to avatar video/audio
                )
            )
            
            return token.to_jwt()
            
        except Exception as e:
            raise Exception(f"Failed to generate access token: {str(e)}")
    
    async def delete_room(self, room_name: str) -> bool:
        """
        Delete a LiveKit room (cleanup after session ends).
        
        Args:
            room_name: Name of the room to delete
            
        Returns:
            True if successful, False otherwise
        """
        try:
            livekit_api = api.LiveKitAPI(
                url=self.livekit_url,
                api_key=self.api_key,
                api_secret=self.api_secret
            )
            
            await livekit_api.room.delete_room(
                api.DeleteRoomRequest(room=room_name)
            )
            return True
            
        except Exception:
            return False
