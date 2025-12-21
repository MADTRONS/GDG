"""Daily.co API service for room and token management."""
import requests
from datetime import datetime, timedelta
from typing import Dict, Optional
from app.config import get_settings

settings = get_settings()


class DailyService:
    """Service for interacting with Daily.co API."""
    
    def __init__(self):
        self.api_key = settings.daily_api_key
        self.base_url = "https://api.daily.co/v1"
        self.headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
    
    async def create_room(self, room_name: str) -> Dict:
        """
        Create a temporary Daily.co room for voice calling.
        
        Args:
            room_name: Unique identifier for the room
            
        Returns:
            Dict with room_url and room configuration
            
        Raises:
            Exception: If Daily.co API call fails
        """
        expires_in_hours = 24
        expires_at = datetime.utcnow() + timedelta(hours=expires_in_hours)
        
        payload = {
            "name": room_name,
            "properties": {
                "enable_chat": True,
                "enable_screenshare": False,
                "max_participants": 2,
                "exp": int(expires_at.timestamp()),
                "enable_recording": False,  # Privacy: no recording by default
                "enable_network_ui": True,  # Show connection quality
            }
        }
        
        try:
            response = requests.post(
                f"{self.base_url}/rooms",
                headers=self.headers,
                json=payload,
                timeout=10
            )
            response.raise_for_status()
            room_data = response.json()
            return {
                "room_url": room_data["url"],
                "room_name": room_data["name"],
                "config": room_data.get("config", {})
            }
        except requests.exceptions.RequestException as e:
            raise Exception(f"Failed to create Daily.co room: {str(e)}")
    
    async def create_user_token(self, room_name: str, user_id: str) -> str:
        """
        Generate a Daily.co meeting token for a student.
        
        Args:
            room_name: Name of the Daily.co room
            user_id: Student''s unique identifier
            
        Returns:
            JWT token for room access
            
        Raises:
            Exception: If token creation fails
        """
        expires_in_hours = 24
        expires_at = datetime.utcnow() + timedelta(hours=expires_in_hours)
        
        payload = {
            "properties": {
                "room_name": room_name,
                "user_name": f"Student_{user_id[:8]}",
                "is_owner": False,
                "enable_recording": False,
                "exp": int(expires_at.timestamp())
            }
        }
        
        try:
            response = requests.post(
                f"{self.base_url}/meeting-tokens",
                headers=self.headers,
                json=payload,
                timeout=10
            )
            response.raise_for_status()
            return response.json()["token"]
        except requests.exceptions.RequestException as e:
            raise Exception(f"Failed to create user token: {str(e)}")
    
    async def create_bot_token(self, room_name: str) -> str:
        """
        Generate a Daily.co meeting token for the PipeCat bot.
        
        Args:
            room_name: Name of the Daily.co room
            
        Returns:
            JWT token for bot room access
            
        Raises:
            Exception: If token creation fails
        """
        expires_in_hours = 24
        expires_at = datetime.utcnow() + timedelta(hours=expires_in_hours)
        
        payload = {
            "properties": {
                "room_name": room_name,
                "user_name": "Counselor",
                "is_owner": True,  # Bot has owner privileges
                "enable_recording": False,
                "exp": int(expires_at.timestamp())
            }
        }
        
        try:
            response = requests.post(
                f"{self.base_url}/meeting-tokens",
                headers=self.headers,
                json=payload,
                timeout=10
            )
            response.raise_for_status()
            return response.json()["token"]
        except requests.exceptions.RequestException as e:
            raise Exception(f"Failed to create bot token: {str(e)}")
    
    async def delete_room(self, room_name: str) -> bool:
        """
        Delete a Daily.co room (cleanup after session ends).
        
        Args:
            room_name: Name of the room to delete
            
        Returns:
            True if deletion successful, False otherwise
        """
        try:
            response = requests.delete(
                f"{self.base_url}/rooms/{room_name}",
                headers=self.headers,
                timeout=10
            )
            response.raise_for_status()
            return True
        except requests.exceptions.RequestException:
            return False
