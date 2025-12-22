"""
Beyond Presence Avatar Agent for Video Counseling Sessions.
Uses Gemini AI + LiveKit + Beyond Presence Avatar.
"""

import asyncio
import os
import sys
import json
from typing import Optional
from loguru import logger
import google.generativeai as genai
from livekit import rtc, api
import websockets

# Configure logging
logger.remove()
logger.add(sys.stderr, level="INFO", format="<green>{time:HH:mm:ss}</green> | <level>{level: <8}</level> | {message}")


class BeyondPresenceAvatarAgent:
    """Video avatar agent using Gemini AI, LiveKit, and Beyond Presence."""
    
    def __init__(self):
        """Initialize agent with environment configuration."""
        # Load environment variables
        self.room_name = os.getenv("ROOM_NAME")
        self.session_id = os.getenv("SESSION_ID")
        self.avatar_id = os.getenv("AVATAR_ID")  # Beyond Presence Avatar ID
        self.avatar_api_key = os.getenv("BEY_AVATAR_API_KEY")  # Beyond Presence API key
        self.system_prompt = os.getenv("SYSTEM_PROMPT")
        self.counselor_category = os.getenv("COUNSELOR_CATEGORY", "General")
        
        # LiveKit configuration
        self.livekit_url = os.getenv("LIVEKIT_URL")
        self.livekit_api_key = os.getenv("LIVEKIT_API_KEY")
        self.livekit_api_secret = os.getenv("LIVEKIT_API_SECRET")
        
        # Gemini configuration
        self.google_api_key = os.getenv("GOOGLE_API_KEY")
        
        # Validate required configuration
        self._validate_config()
        
        # Initialize components
        self.room: Optional[rtc.Room] = None
        self.conversation_history = []
        
        logger.info(f"=== Initializing Beyond Presence Avatar Agent ===")
        logger.info(f"Session ID: {self.session_id}")
        logger.info(f"Category: {self.counselor_category}")
        logger.info(f"Avatar ID: {self.avatar_id}")
        logger.info(f"Room: {self.room_name}")
    
    def _validate_config(self):
        """Validate all required environment variables are present."""
        required_vars = {
            "ROOM_NAME": self.room_name,
            "SESSION_ID": self.session_id,
            "AVATAR_ID": self.avatar_id,
            "BEY_AVATAR_API_KEY": self.avatar_api_key,
            "SYSTEM_PROMPT": self.system_prompt,
            "LIVEKIT_URL": self.livekit_url,
            "LIVEKIT_API_KEY": self.livekit_api_key,
            "LIVEKIT_API_SECRET": self.livekit_api_secret,
            "GOOGLE_API_KEY": self.google_api_key,
        }
        
        missing = [key for key, value in required_vars.items() if not value]
        if missing:
            raise ValueError(f"Missing required environment variables: {', '.join(missing)}")
    
    async def connect_to_livekit(self):
        """Connect to LiveKit room as avatar agent."""
        logger.info("Connecting to LiveKit room...")
        
        # Generate access token for agent
        token = api.AccessToken(self.livekit_api_key, self.livekit_api_secret)
        token.with_identity(f"avatar-agent-{self.session_id}")
        token.with_name(f"{self.counselor_category} Counselor")
        token.with_grants(api.VideoGrants(
            room_join=True,
            room=self.room_name,
            can_publish=True,
            can_subscribe=True,
        ))
        
        # Connect to room
        self.room = rtc.Room()
        
        # Set up event handlers
        @self.room.on("participant_connected")
        def on_participant_connected(participant: rtc.RemoteParticipant):
            logger.info(f"Student participant connected: {participant.identity}")
        
        @self.room.on("track_subscribed")
        def on_track_subscribed(track: rtc.Track, publication: rtc.TrackPublication, participant: rtc.RemoteParticipant):
            logger.info(f"Track subscribed: {track.kind} from {participant.identity}")
            if track.kind == rtc.TrackKind.KIND_AUDIO:
                asyncio.create_task(self._handle_audio_track(track, participant))
        
        await self.room.connect(self.livekit_url, token.to_jwt())
        logger.info(f"Successfully connected to room: {self.room_name}")
    
    def initialize_gemini(self):
        """Initialize Gemini AI model."""
        logger.info("Initializing Gemini AI...")
        genai.configure(api_key=self.google_api_key)
        
        # Configure Gemini model for conversation
        self.model = genai.GenerativeModel(
            model_name='gemini-pro',
            generation_config={
                'temperature': 0.7,
                'top_p': 0.95,
                'top_k': 40,
                'max_output_tokens': 1024,
            }
        )
        
        # Start conversation with system prompt
        self.chat = self.model.start_chat(history=[])
        
        # Send system prompt as first message (Gemini doesn't have system role, so we use user message)
        logger.info("Loading system prompt for counselor persona...")
        logger.debug(f"System prompt length: {len(self.system_prompt)} characters")
    
    async def initialize_avatar(self):
        """Initialize Beyond Presence avatar connection."""
        logger.info("Initializing Beyond Presence avatar...")
        logger.info(f"Using Avatar ID: {self.avatar_id}")
        
        # Note: Beyond Presence integration would go here
        # This is a placeholder for actual Beyond Presence SDK integration
        # The avatar rendering would typically involve:
        # 1. WebSocket connection to Beyond Presence service
        # 2. Sending avatar configuration (ID, API key)
        # 3. Streaming avatar video frames to LiveKit
        # 4. Syncing lip movements with audio
        
        logger.warning("Beyond Presence avatar integration is placeholder - SDK integration pending")
        logger.info("Avatar initialized (placeholder mode)")
    
    async def send_greeting(self):
        """Send category-appropriate greeting to student."""
        greetings = {
            "Health": "Hi there! I'm here to support your health and wellness. What's on your mind today?",
            "Career": "Hello! I'm excited to help you explore your career path. What brings you in?",
            "Academic": "Hi! I'm here to help with your studies. What can I assist you with today?",
            "Financial Aid": "Hello! I'm here to help you navigate financial aid. What questions do you have?",
            "Social": "Hi! Let's talk about building connections and campus life. What's up?",
            "Personal Development": "Hello! I'm here to support your personal growth journey. What would you like to work on?"
        }
        
        greeting = greetings.get(self.counselor_category, "Hello! How can I help you today?")
        logger.info(f"Sending greeting: {greeting}")
        
        # Send greeting through Gemini to start conversation context
        response = await self._get_gemini_response(
            f"[System: You are starting a counseling session. Greet the student with: '{greeting}']"
        )
        
        # Publish audio track with greeting
        await self._publish_text_as_audio(greeting)
    
    async def _get_gemini_response(self, message: str) -> str:
        """Get response from Gemini AI."""
        try:
            # Include system prompt context in first turn
            if len(self.conversation_history) == 0:
                full_message = f"{self.system_prompt}\n\nStudent: {message}"
            else:
                full_message = f"Student: {message}"
            
            self.conversation_history.append({"role": "user", "content": message})
            
            # Get response from Gemini
            response = await asyncio.to_thread(
                lambda: self.chat.send_message(full_message)
            )
            
            response_text = response.text
            self.conversation_history.append({"role": "assistant", "content": response_text})
            
            logger.info(f"Gemini response: {response_text[:100]}...")
            return response_text
            
        except Exception as e:
            logger.error(f"Error getting Gemini response: {e}")
            return "I apologize, I\'m having trouble processing that right now. Could you please rephrase?"
    
    async def _publish_text_as_audio(self, text: str):
        """Convert text to speech and publish as audio track."""
        logger.info(f"Publishing audio: {text[:50]}...")
        
        # Note: This would integrate with Google TTS or another TTS service
        # For now, this is a placeholder
        # Actual implementation would:
        # 1. Convert text to speech using Google TTS API
        # 2. Create audio track from TTS output
        # 3. Publish to LiveKit room
        # 4. Sync with Beyond Presence avatar lip movements
        
        logger.warning("TTS audio publishing is placeholder - requires Google TTS integration")
    
    async def _handle_audio_track(self, track: rtc.AudioTrack, participant: rtc.RemoteParticipant):
        """Handle incoming audio from student."""
        logger.info(f"Handling audio track from {participant.identity}")
        
        # Note: This would integrate with audio transcription (e.g., Deepgram)
        # For now, this is a placeholder
        # Actual implementation would:
        # 1. Stream audio frames from track
        # 2. Send to transcription service (Deepgram, Google Speech-to-Text)
        # 3. Get text transcription
        # 4. Send to Gemini for response
        # 5. Convert response to speech
        # 6. Publish audio with avatar lip-sync
        
        logger.warning("Audio transcription is placeholder - requires Deepgram or Google STT integration")
    
    async def run(self):
        """Main agent loop."""
        try:
            # Initialize components
            await self.connect_to_livekit()
            self.initialize_gemini()
            await self.initialize_avatar()
            
            # Wait for student to join
            logger.info("Waiting for student to join...")
            await asyncio.sleep(2)  # Give time for participant to connect
            
            # Send greeting
            await self.send_greeting()
            
            # Keep session active
            logger.info("Avatar agent active and ready for conversation")
            logger.info("Conversation loop started (placeholder mode)")
            
            # Stay connected until room is disconnected
            while self.room and self.room.connection_state == rtc.ConnectionState.CONN_CONNECTED:
                await asyncio.sleep(1)
            
            logger.info("Room disconnected, ending session")
            
        except Exception as e:
            logger.error(f"Fatal error in agent: {e}", exc_info=True)
            raise
        finally:
            await self.cleanup()
    
    async def cleanup(self):
        """Clean up resources."""
        logger.info("Cleaning up resources...")
        
        if self.room:
            await self.room.disconnect()
        
        logger.info("Agent shutdown complete")


async def main():
    """Entry point for avatar agent process."""
    logger.info("=" * 60)
    logger.info("Beyond Presence Avatar Agent Starting")
    logger.info("=" * 60)
    
    try:
        agent = BeyondPresenceAvatarAgent()
        await agent.run()
        
    except KeyboardInterrupt:
        logger.info("Agent interrupted by user (Ctrl+C)")
    except ValueError as e:
        logger.error(f"Configuration error: {e}")
        sys.exit(1)
    except Exception as e:
        logger.error(f"Fatal error: {e}", exc_info=True)
        sys.exit(1)
    
    logger.info("=" * 60)
    logger.info("Beyond Presence Avatar Agent Exited")
    logger.info("=" * 60)


if __name__ == "__main__":
    asyncio.run(main())
