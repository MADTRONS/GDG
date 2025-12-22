"""Service for spawning and managing Beyond Presence avatar agents."""
import asyncio
import os
import subprocess
from typing import Dict
from uuid import UUID

from app.config import get_settings
from app.repositories.counselor_repository import CounselorRepository


class AvatarService:
    """Service for spawning Beyond Presence avatar agents for video sessions."""
    
    def __init__(self, counselor_repo: CounselorRepository):
        """
        Initialize avatar service.
        
        Args:
            counselor_repo: Repository for accessing counselor categories
        """
        self.counselor_repo = counselor_repo
    
    async def spawn_avatar(
        self,
        room_name: str,
        session_id: str,
        category_id: str
    ) -> Dict[str, any]:
        """
        Spawn a Beyond Presence avatar agent for a video session.
        
        Args:
            room_name: LiveKit room name
            session_id: Unique session identifier
            category_id: Counselor category UUID string
            
        Returns:
            Dict with agent process information
            
        Raises:
            ValueError: If counselor category is invalid
            Exception: If avatar spawn fails
        """
        # Get category system prompt
        category = await self.counselor_repo.get_by_id(UUID(category_id))
        if not category:
            raise ValueError(f"Invalid counselor category: {category_id}")
        
        system_prompt = category.system_prompt or self._get_default_prompt()
        
        # Get settings
        settings = get_settings()
        
        # Prepare environment variables for avatar agent process
        env = os.environ.copy()
        env.update({
            "LIVEKIT_URL": settings.livekit_url,
            "LIVEKIT_API_KEY": settings.livekit_api_key,
            "LIVEKIT_API_SECRET": settings.livekit_api_secret,
            "ROOM_NAME": room_name,
            "SESSION_ID": session_id,
            "AVATAR_ID": settings.bey_avatar_id,  # Beyond Presence avatar ID
            "OPENAI_API_KEY": settings.openai_api_key,
            "SYSTEM_PROMPT": system_prompt,
            "COUNSELOR_CATEGORY": category.name
        })
        
        # Path to avatar agent script
        agent_script_path = os.path.join(
            os.path.dirname(__file__),
            "..", "..", "avatar_agent", "video_agent.py"
        )
        
        try:
            # Spawn agent as background process
            process = subprocess.Popen(
                ["python", agent_script_path],
                env=env,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                start_new_session=True
            )
            
            return {
                "process_id": process.pid,
                "session_id": session_id,
                "status": "spawned"
            }
            
        except Exception as e:
            raise Exception(f"Failed to spawn avatar agent: {str(e)}")
    
    def _get_default_prompt(self) -> str:
        """Fallback system prompt if category doesn't have one."""
        return """You are a supportive counselor helping college students via video. 
        Maintain warm facial expressions and make eye contact. 
        Be empathetic, professional, and non-judgmental. 
        Ask clarifying questions and provide actionable guidance."""
