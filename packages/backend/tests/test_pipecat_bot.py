"""Tests for PipeCat voice bot implementation"""
import os
import pytest
from unittest.mock import Mock, patch, AsyncMock, MagicMock
from pipecat_bot.voice_bot import VoiceCounselorBot
from pipecat_bot.system_prompts import get_system_prompt, SYSTEM_PROMPTS


class TestVoiceCounselorBotInitialization:
    """Test bot initialization and configuration"""

    def test_bot_requires_all_environment_variables(self, monkeypatch):
        """Bot should raise ValueError if required env vars missing"""
        # Clear all env vars
        for key in ["DAILY_ROOM_URL", "DAILY_TOKEN", "SESSION_ID", "SYSTEM_PROMPT",
                    "DEEPGRAM_API_KEY", "CARTESIA_API_KEY", "GOOGLE_API_KEY", "OPENAI_API_KEY"]:
            monkeypatch.delenv(key, raising=False)
        
        # Set minimal required
        monkeypatch.setenv("DEEPGRAM_API_KEY", "test_key")
        monkeypatch.setenv("CARTESIA_API_KEY", "test_key")
        monkeypatch.setenv("GOOGLE_API_KEY", "test_key")
        
        with pytest.raises(ValueError, match="Missing required environment variables"):
            VoiceCounselorBot()

    def test_bot_requires_at_least_one_llm_key(self, monkeypatch):
        """Bot should require either Google or OpenAI API key"""
        # Set all required except LLM keys
        monkeypatch.setenv("DAILY_ROOM_URL", "https://test.daily.co/room")
        monkeypatch.setenv("DAILY_TOKEN", "test_token")
        monkeypatch.setenv("SESSION_ID", "test_session")
        monkeypatch.setenv("SYSTEM_PROMPT", "Test prompt")
        monkeypatch.setenv("DEEPGRAM_API_KEY", "test_key")
        monkeypatch.setenv("CARTESIA_API_KEY", "test_key")
        monkeypatch.delenv("GOOGLE_API_KEY", raising=False)
        monkeypatch.delenv("OPENAI_API_KEY", raising=False)
        
        with pytest.raises(ValueError, match="Must provide either GOOGLE_API_KEY or OPENAI_API_KEY"):
            VoiceCounselorBot()

    def test_bot_initializes_with_valid_config(self, monkeypatch):
        """Bot should initialize successfully with all required env vars"""
        monkeypatch.setenv("DAILY_ROOM_URL", "https://test.daily.co/room")
        monkeypatch.setenv("DAILY_TOKEN", "test_token")
        monkeypatch.setenv("SESSION_ID", "test_session_123")
        monkeypatch.setenv("SYSTEM_PROMPT", "You are a helpful counselor")
        monkeypatch.setenv("COUNSELOR_CATEGORY", "Health")
        monkeypatch.setenv("DEEPGRAM_API_KEY", "dg_test_key")
        monkeypatch.setenv("CARTESIA_API_KEY", "cart_test_key")
        monkeypatch.setenv("GOOGLE_API_KEY", "google_test_key")
        monkeypatch.setenv("OPENAI_API_KEY", "openai_test_key")
        
        bot = VoiceCounselorBot()
        
        assert bot.room_url == "https://test.daily.co/room"
        assert bot.token == "test_token"
        assert bot.session_id == "test_session_123"
        assert bot.system_prompt == "You are a helpful counselor"
        assert bot.counselor_category == "Health"
        assert bot.deepgram_api_key == "dg_test_key"
        assert bot.cartesia_api_key == "cart_test_key"
        assert bot.google_api_key == "google_test_key"
        assert bot.openai_api_key == "openai_test_key"

    def test_bot_defaults_category_to_general(self, monkeypatch):
        """Bot should default to General category if not specified"""
        monkeypatch.setenv("DAILY_ROOM_URL", "https://test.daily.co/room")
        monkeypatch.setenv("DAILY_TOKEN", "test_token")
        monkeypatch.setenv("SESSION_ID", "test_session")
        monkeypatch.setenv("SYSTEM_PROMPT", "Test prompt")
        monkeypatch.setenv("DEEPGRAM_API_KEY", "test_key")
        monkeypatch.setenv("CARTESIA_API_KEY", "test_key")
        monkeypatch.setenv("GOOGLE_API_KEY", "test_key")
        monkeypatch.delenv("COUNSELOR_CATEGORY", raising=False)
        
        bot = VoiceCounselorBot()
        assert bot.counselor_category == "General"


class TestVoiceCounselorBotServices:
    """Test bot service initialization"""

    @pytest.fixture
    def mock_env(self, monkeypatch):
        """Setup mock environment variables"""
        monkeypatch.setenv("DAILY_ROOM_URL", "https://test.daily.co/room")
        monkeypatch.setenv("DAILY_TOKEN", "test_token")
        monkeypatch.setenv("SESSION_ID", "test_session")
        monkeypatch.setenv("SYSTEM_PROMPT", "Test prompt")
        monkeypatch.setenv("COUNSELOR_CATEGORY", "Career")
        monkeypatch.setenv("DEEPGRAM_API_KEY", "dg_key")
        monkeypatch.setenv("CARTESIA_API_KEY", "cart_key")
        monkeypatch.setenv("GOOGLE_API_KEY", "google_key")
        monkeypatch.setenv("OPENAI_API_KEY", "openai_key")

    @pytest.mark.asyncio
    @patch('pipecat_bot.voice_bot.DailyTransport')
    @patch('pipecat_bot.voice_bot.DeepgramSTTService')
    @patch('pipecat_bot.voice_bot.CartesiaTTSService')
    @patch('pipecat_bot.voice_bot.OpenAILLMService')
    async def test_service_initialization(self, mock_openai, mock_tts, mock_stt, 
                                         mock_transport, mock_env):
        """Bot should initialize all required services"""
        bot = VoiceCounselorBot()
        await bot.initialize_services()
        
        # Verify Daily transport initialized
        mock_transport.assert_called_once()
        call_args = mock_transport.call_args
        assert call_args[0][0] == "https://test.daily.co/room"
        assert call_args[0][1] == "test_token"
        assert call_args[0][2] == "VoiceBot"
        
        # Verify Deepgram STT initialized
        mock_stt.assert_called_once()
        stt_call = mock_stt.call_args
        assert stt_call[1]['api_key'] == "dg_key"
        assert stt_call[1]['params']['model'] == "nova-2"
        
        # Verify Cartesia TTS initialized
        mock_tts.assert_called_once()
        tts_call = mock_tts.call_args
        assert tts_call[1]['api_key'] == "cart_key"
        assert tts_call[1]['voice_id'] == "sonic-english"


class TestVoiceCounselorBotPipeline:
    """Test pipeline building"""

    @pytest.fixture
    def bot_with_services(self, monkeypatch):
        """Create bot with mocked services"""
        monkeypatch.setenv("DAILY_ROOM_URL", "https://test.daily.co/room")
        monkeypatch.setenv("DAILY_TOKEN", "test_token")
        monkeypatch.setenv("SESSION_ID", "test_session")
        monkeypatch.setenv("SYSTEM_PROMPT", "Test prompt")
        monkeypatch.setenv("DEEPGRAM_API_KEY", "dg_key")
        monkeypatch.setenv("CARTESIA_API_KEY", "cart_key")
        monkeypatch.setenv("GOOGLE_API_KEY", "google_key")
        
        bot = VoiceCounselorBot()
        bot.transport = Mock()
        bot.transport.input_audio = Mock(return_value="input_audio")
        bot.transport.output_audio = Mock(return_value="output_audio")
        bot.stt = Mock()
        bot.tts = Mock()
        bot.llm = Mock()
        return bot

    @patch('pipecat_bot.voice_bot.LLMResponseAggregator')
    @patch('pipecat_bot.voice_bot.Pipeline')
    def test_pipeline_builds_correctly(self, mock_pipeline, mock_aggregator, bot_with_services):
        """Pipeline should be built with correct component order"""
        bot = bot_with_services
        bot.build_pipeline()
        
        # Verify aggregator created
        mock_aggregator.assert_called_once()
        
        # Verify pipeline created with components
        mock_pipeline.assert_called_once()
        pipeline_components = mock_pipeline.call_args[0][0]
        
        assert pipeline_components[0] == "input_audio"
        assert pipeline_components[1] == bot.stt
        assert pipeline_components[2] == bot.llm
        # aggregator at position 3
        assert pipeline_components[4] == bot.tts
        assert pipeline_components[5] == "output_audio"


class TestVoiceCounselorBotGreetings:
    """Test category-specific greetings"""

    @pytest.fixture
    def bot(self, monkeypatch):
        """Create bot with minimal config"""
        monkeypatch.setenv("DAILY_ROOM_URL", "https://test.daily.co/room")
        monkeypatch.setenv("DAILY_TOKEN", "test_token")
        monkeypatch.setenv("SESSION_ID", "test_session")
        monkeypatch.setenv("SYSTEM_PROMPT", "Test prompt")
        monkeypatch.setenv("DEEPGRAM_API_KEY", "dg_key")
        monkeypatch.setenv("CARTESIA_API_KEY", "cart_key")
        monkeypatch.setenv("GOOGLE_API_KEY", "google_key")
        return VoiceCounselorBot

    def test_health_greeting(self, bot, monkeypatch):
        """Health category should have wellness-focused greeting"""
        monkeypatch.setenv("COUNSELOR_CATEGORY", "Health")
        b = bot()
        greeting = b._get_greeting()
        assert "health" in greeting.lower() or "wellness" in greeting.lower()

    def test_career_greeting(self, bot, monkeypatch):
        """Career category should have career-focused greeting"""
        monkeypatch.setenv("COUNSELOR_CATEGORY", "Career")
        b = bot()
        greeting = b._get_greeting()
        assert "career" in greeting.lower()

    def test_default_greeting(self, bot, monkeypatch):
        """Unknown category should use default greeting"""
        monkeypatch.setenv("COUNSELOR_CATEGORY", "Unknown")
        b = bot()
        greeting = b._get_greeting()
        assert "support you" in greeting


class TestSystemPrompts:
    """Test system prompts module"""

    def test_all_categories_have_prompts(self):
        """All 6 counselor categories should have system prompts"""
        required_categories = ["Health", "Career", "Academic", "Financial Aid", 
                              "Social", "Personal Development"]
        
        for category in required_categories:
            assert category in SYSTEM_PROMPTS
            prompt = SYSTEM_PROMPTS[category]
            assert len(prompt) > 100  # Prompts should be substantial
            assert "Guidelines" in prompt or "guidelines" in prompt

    def test_get_system_prompt_returns_correct_prompt(self):
        """get_system_prompt should return correct prompt for category"""
        health_prompt = get_system_prompt("Health")
        assert "Health" in health_prompt or "wellness" in health_prompt
        
        career_prompt = get_system_prompt("Career")
        assert "Career" in career_prompt or "career" in career_prompt

    def test_get_system_prompt_defaults_to_personal_development(self):
        """Unknown categories should default to Personal Development"""
        unknown_prompt = get_system_prompt("Unknown Category")
        expected = SYSTEM_PROMPTS["Personal Development"]
        assert unknown_prompt == expected

    def test_health_prompt_includes_crisis_guidelines(self):
        """Health prompt should include crisis detection guidelines"""
        health_prompt = SYSTEM_PROMPTS["Health"]
        assert "crisis" in health_prompt.lower()
        assert "escalate" in health_prompt.lower() or "emergency" in health_prompt.lower()

    def test_prompts_include_context_sections(self):
        """All prompts should include Context section"""
        for category, prompt in SYSTEM_PROMPTS.items():
            assert "Context:" in prompt, f"{category} missing Context section"

    def test_prompts_include_example_responses(self):
        """All prompts should include Example Response Style"""
        for category, prompt in SYSTEM_PROMPTS.items():
            assert "Example Response" in prompt, f"{category} missing examples"
