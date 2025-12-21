"""PipeCat bot service for spawning voice AI agents."""
import os
import subprocess
from typing import Dict
from app.config import get_settings
from app.repositories.counselor_repository import CounselorRepository

settings = get_settings()


class PipeCatService:
    """Service for spawning and managing PipeCat bot instances."""
    
    def __init__(self, counselor_repo: CounselorRepository):
        self.counselor_repo = counselor_repo
    
    async def spawn_bot(
        self,
        room_url: str,
        bot_token: str,
        session_id: str,
        category_id: str
    ) -> Dict:
        """
        Spawn a PipeCat bot instance for a voice session.
        
        Args:
            room_url: Daily.co room URL
            bot_token: Authentication token for bot
            session_id: Unique session identifier
            category_id: Counselor category UUID
            
        Returns:
            Dict with bot process information
            
        Raises:
            ValueError: If category is invalid
            Exception: If bot spawn fails
        """
        # Get category
        category = await self.counselor_repo.get_by_id(category_id)
        if not category:
            raise ValueError(f"Invalid counselor category: {category_id}")
        
        # Get system prompt (use default for now)
        system_prompt = self._get_category_prompt(category.name)
        
        # Prepare environment variables for bot process
        env = os.environ.copy()
        env.update({
            "DAILY_ROOM_URL": room_url,
            "DAILY_TOKEN": bot_token,
            "SESSION_ID": session_id,
            "DEEPGRAM_API_KEY": settings.deepgram_api_key,
            "CARTESIA_API_KEY": settings.cartesia_api_key,
            "GOOGLE_API_KEY": settings.google_api_key,
            "OPENAI_API_KEY": settings.openai_api_key,
            "SYSTEM_PROMPT": system_prompt,
            "COUNSELOR_CATEGORY": category.name
        })
        
        # Path to PipeCat bot script (will be created in Story 3.2)
        bot_script_path = os.path.join(
            os.path.dirname(__file__),
            "..", "..", "pipecat_bot", "voice_bot.py"
        )
        
        try:
            # Spawn bot as background process
            process = subprocess.Popen(
                ["python", bot_script_path],
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
            raise Exception(f"Failed to spawn PipeCat bot: {str(e)}")
    
    def _get_category_prompt(self, category_name: str) -> str:
        """Get category-specific system prompt."""
        prompts = {
            "Health & Wellness": """You are a supportive health and wellness counselor for college students.
Focus on physical health, mental well-being, stress management, and healthy lifestyle choices.
Be empathetic, non-judgmental, and encourage professional help when needed.
Ask clarifying questions and provide actionable guidance.""",
            
            "Academic Support": """You are an academic counselor helping college students with their studies.
Focus on study strategies, time management, course selection, and academic goals.
Be encouraging, provide practical advice, and help students develop effective learning habits.
Ask about specific challenges and offer concrete solutions.""",
            
            "Career Guidance": """You are a career counselor helping college students explore their future.
Focus on career exploration, internship opportunities, resume building, and interview preparation.
Be supportive, help identify strengths, and provide realistic career guidance.
Ask about interests, skills, and goals to provide personalized advice.""",
            
            "Personal Growth": """You are a personal development counselor for college students.
Focus on self-discovery, confidence building, relationship skills, and life transitions.
Be compassionate, help students explore their values and goals.
Ask reflective questions and provide supportive guidance.""",
            
            "Financial Aid": """You are a financial aid counselor helping college students with financial matters.
Focus on budgeting, student loans, scholarships, and financial planning.
Be informative, provide practical financial advice, and help reduce financial stress.
Ask about specific financial concerns and offer actionable solutions."""
        }
        
        return prompts.get(category_name, self._get_default_prompt())
    
    def _get_default_prompt(self) -> str:
        """Fallback system prompt if category doesn''t have a specific one."""
        return """You are a supportive counselor helping college students. 
Be empathetic, professional, and non-judgmental. 
Listen actively, ask clarifying questions, and provide actionable guidance.
If the student''s concerns require professional help, encourage them to seek appropriate resources."""
