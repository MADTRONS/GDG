import asyncio
import os
import sys
from loguru import logger
from pipecat.frames.frames import EndFrame
from pipecat.pipeline.pipeline import Pipeline
from pipecat.pipeline.runner import PipelineRunner
from pipecat.pipeline.task import PipelineTask
from pipecat.services.deepgram.stt import DeepgramSTTService
from pipecat.services.cartesia.tts import CartesiaTTSService
from pipecat.services.openai.llm import OpenAILLMService
from pipecat.transports.services.daily import DailyTransport, DailyParams
from pipecat.processors.aggregators.llm_response import LLMResponseAggregator

# Configure logger
logger.remove()
logger.add(sys.stderr, level="INFO")


class VoiceCounselorBot:
    """PipeCat voice counselor bot for student therapy sessions"""

    def __init__(self):
        """Initialize bot and validate environment variables"""
        logger.info("Initializing VoiceCounselorBot")
        
        # Required environment variables
        self.room_url = os.getenv("DAILY_ROOM_URL")
        self.token = os.getenv("DAILY_TOKEN")
        self.session_id = os.getenv("SESSION_ID")
        self.system_prompt = os.getenv("SYSTEM_PROMPT")
        self.counselor_category = os.getenv("COUNSELOR_CATEGORY", "General")
        
        # API keys
        self.deepgram_api_key = os.getenv("DEEPGRAM_API_KEY")
        self.cartesia_api_key = os.getenv("CARTESIA_API_KEY")
        self.google_api_key = os.getenv("GOOGLE_API_KEY")
        self.openai_api_key = os.getenv("OPENAI_API_KEY")
        
        # Validate required config
        if not all([
            self.room_url,
            self.token,
            self.session_id,
            self.system_prompt,
            self.deepgram_api_key,
            self.cartesia_api_key
        ]):
            missing = []
            if not self.room_url: missing.append("DAILY_ROOM_URL")
            if not self.token: missing.append("DAILY_TOKEN")
            if not self.session_id: missing.append("SESSION_ID")
            if not self.system_prompt: missing.append("SYSTEM_PROMPT")
            if not self.deepgram_api_key: missing.append("DEEPGRAM_API_KEY")
            if not self.cartesia_api_key: missing.append("CARTESIA_API_KEY")
            
            raise ValueError(f"Missing required environment variables: {', '.join(missing)}")
        
        # Validate LLM keys (need at least one)
        if not self.google_api_key and not self.openai_api_key:
            raise ValueError("Must provide either GOOGLE_API_KEY or OPENAI_API_KEY")
        
        logger.info(f"Bot configured for session {self.session_id} in category {self.counselor_category}")
        
        # Services
        self.transport = None
        self.stt = None
        self.tts = None
        self.llm = None
        self.fallback_llm = None
        self.pipeline = None
        self.runner = None

    async def initialize_services(self):
        """Initialize PipeCat services"""
        logger.info("Initializing PipeCat services")
        
        try:
            # Initialize Daily transport
            self.transport = DailyTransport(
                self.room_url,
                self.token,
                "VoiceBot",
                DailyParams(
                    audio_in_enabled=True,
                    audio_out_enabled=True,
                    transcription_enabled=False  # We handle STT ourselves
                )
            )
            
            # Initialize Deepgram STT (Nova-2 model)
            self.stt = DeepgramSTTService(
                api_key=self.deepgram_api_key,
                params={
                    "model": "nova-2",
                    "language": "en-US",
                    "smart_format": True,
                    "punctuate": True
                }
            )
            
            # Initialize Cartesia TTS (Sonic English voice)
            self.tts = CartesiaTTSService(
                api_key=self.cartesia_api_key,
                voice_id="sonic-english",  # Warm, empathetic voice
                params={
                    "model": "sonic-english",
                    "speed": "normal"
                }
            )
            
            # Initialize primary LLM (Google Gemini if available, otherwise OpenAI)
            if self.google_api_key:
                try:
                    from pipecat.services.google import GoogleLLMService
                    self.llm = GoogleLLMService(
                        api_key=self.google_api_key,
                        model="gemini-2.0-flash-exp",
                        params={
                            "temperature": 0.7,
                            "system_instruction": self.system_prompt
                        }
                    )
                    logger.info("Primary LLM: Google Gemini 2.0 Flash")
                except ImportError:
                    logger.warning("Google LLM not available, falling back to OpenAI")
                    self.llm = None
            
            # Initialize OpenAI LLM (primary or fallback)
            if not self.llm:
                if not self.openai_api_key:
                    raise ValueError("OpenAI API key required when Google LLM unavailable")
                self.llm = OpenAILLMService(
                    api_key=self.openai_api_key,
                    model="gpt-4",
                    params={
                        "temperature": 0.7,
                        "messages": [{"role": "system", "content": self.system_prompt}]
                    }
                )
                logger.info("Primary LLM: OpenAI GPT-4")
            elif self.openai_api_key:
                # Setup OpenAI as fallback
                self.fallback_llm = OpenAILLMService(
                    api_key=self.openai_api_key,
                    model="gpt-4",
                    params={
                        "temperature": 0.7,
                        "messages": [{"role": "system", "content": self.system_prompt}]
                    }
                )
                logger.info("Fallback LLM: OpenAI GPT-4")
            
            logger.info("All services initialized successfully")
            
        except Exception as e:
            logger.error(f"Failed to initialize services: {e}")
            raise

    def build_pipeline(self):
        """Build PipeCat conversation pipeline"""
        logger.info("Building conversation pipeline")
        
        try:
            # Create aggregator for streaming LLM responses
            aggregator = LLMResponseAggregator()
            
            # Build pipeline: audio_in  STT  LLM  aggregator  TTS  audio_out
            self.pipeline = Pipeline([
                self.transport.input_audio(),
                self.stt,
                self.llm,
                aggregator,
                self.tts,
                self.transport.output_audio()
            ])
            
            logger.info("Pipeline built successfully")
            
        except Exception as e:
            logger.error(f"Failed to build pipeline: {e}")
            raise

    async def run(self):
        """Run the bot and handle conversation"""
        logger.info(f"Starting bot for session {self.session_id}")
        
        try:
            # Create pipeline task
            task = PipelineTask(self.pipeline)
            
            # Create and configure runner
            self.runner = PipelineRunner()
            
            # Connect to Daily room
            await self.transport.run(task)
            
            # Send greeting message
            greeting = self._get_greeting()
            logger.info(f"Sending greeting: {greeting}")
            await task.queue_frame({"role": "assistant", "content": greeting})
            
            # Run until session ends
            logger.info("Bot is now active and listening")
            await self.runner.run(task)
            
        except KeyboardInterrupt:
            logger.info("Bot interrupted by user")
        except Exception as e:
            logger.error(f"Bot error: {e}")
            
            # Try fallback LLM if primary fails
            if self.fallback_llm and "google" in str(type(self.llm)).lower():
                logger.info("Attempting fallback to OpenAI")
                try:
                    self.llm = self.fallback_llm
                    self.build_pipeline()
                    task = PipelineTask(self.pipeline)
                    await self.runner.run(task)
                except Exception as fallback_error:
                    logger.error(f"Fallback also failed: {fallback_error}")
                    raise
            else:
                raise
        finally:
            await self.cleanup()

    async def cleanup(self):
        """Gracefully shutdown bot services"""
        logger.info("Cleaning up bot services")
        
        try:
            if self.runner:
                await self.runner.stop()
            
            if self.transport:
                await self.transport.stop()
            
            if self.stt:
                await self.stt.stop()
            
            if self.tts:
                await self.tts.stop()
            
            if self.llm:
                await self.llm.stop()
            
            logger.info("Cleanup completed successfully")
            
        except Exception as e:
            logger.error(f"Error during cleanup: {e}")

    def _get_greeting(self) -> str:
        """Get category-specific greeting message"""
        greetings = {
            "Health": "Hello! I'm here to support your health and wellness journey. How are you feeling today?",
            "Career": "Hi! I'm your career counselor. I'm here to help you explore your professional path. What's on your mind?",
            "Academic": "Hello! I'm here to help with your academic concerns. What would you like to talk about?",
            "Financial Aid": "Hi! I can help you navigate financial aid and resources. What questions do you have?",
            "Social": "Hello! I'm here to talk about social connections and relationships. How can I support you?",
            "Personal Development": "Hi! I'm here to support your personal growth journey. What would you like to explore?"
        }
        return greetings.get(self.counselor_category, "Hello! I'm here to support you. How can I help today?")


async def main():
    """Main entry point"""
    try:
        bot = VoiceCounselorBot()
        await bot.initialize_services()
        bot.build_pipeline()
        await bot.run()
    except Exception as e:
        logger.error(f"Fatal error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    asyncio.run(main())
