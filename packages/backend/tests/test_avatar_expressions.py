"""
Tests for Avatar Emotional Expressions and Lip-Sync
Story 4.5: Avatar Lip-Sync and Emotional Expressions
"""

import pytest
import asyncio
import time
from unittest.mock import Mock, AsyncMock, patch, MagicMock

# Import avatar modules
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'avatar_agent'))

from avatar_config import (
    EmotionalExpression,
    EXPRESSION_PRESETS,
    LIP_SYNC_CONFIG,
    EYE_CONTACT_CONFIG,
    TRANSITION_CONFIG,
    QUALITY_ADAPTATION_CONFIG,
    CRISIS_KEYWORDS,
    POSITIVE_KEYWORDS,
)
from beyond_presence import AvatarSession


class TestAvatarSession:
    """Test Beyond Presence Avatar Session mock"""
    
    @pytest.mark.asyncio
    async def test_avatar_session_initialization(self):
        """Test avatar session initializes with correct configuration"""
        session = AvatarSession(
            avatar_id="test-avatar",
            api_key="test-key",
            lip_sync=LIP_SYNC_CONFIG,
            eye_contact=EYE_CONTACT_CONFIG,
            video_config={"resolution": "720p", "fps": 30},
            enable_expressions=True,
            expression_presets=EXPRESSION_PRESETS,
            transition_config=TRANSITION_CONFIG,
        )
        
        assert session.avatar_id == "test-avatar"
        assert session.api_key == "test-key"
        assert session.enable_expressions is True
        assert session.connected is False
        assert session.animation_quality == "high"
    
    @pytest.mark.asyncio
    async def test_avatar_session_connect(self):
        """Test avatar session connects successfully"""
        session = AvatarSession(
            avatar_id="test-avatar",
            api_key="test-key",
            lip_sync=LIP_SYNC_CONFIG,
            eye_contact=EYE_CONTACT_CONFIG,
            video_config={},
        )
        
        await session.connect()
        assert session.connected is True
    
    @pytest.mark.asyncio
    async def test_set_expression(self):
        """Test setting avatar expression"""
        session = AvatarSession(
            avatar_id="test-avatar",
            api_key="test-key",
            lip_sync={},
            eye_contact={},
            video_config={},
        )
        
        await session.connect()
        
        preset = EXPRESSION_PRESETS[EmotionalExpression.SUPPORTIVE]
        start_time = time.time()
        
        await session.set_expression(
            facial_config=preset["facial_config"],
            body_language=preset["body_language"],
            animation=preset["animation"],
            transition_duration=400
        )
        
        end_time = time.time()
        duration_ms = (end_time - start_time) * 1000
        
        # Verify transition took approximately correct time (within 100ms tolerance)
        assert 300 <= duration_ms <= 500
    
    @pytest.mark.asyncio
    async def test_lipsync_accuracy(self):
        """Test lip-sync accuracy configuration within 50ms threshold (AC1, AC9)"""
        session = AvatarSession(
            avatar_id="test-avatar",
            api_key="test-key",
            lip_sync={"sync_threshold_ms": 50, "accuracy_mode": "high"},
            eye_contact={},
            video_config={}
        )
        
        await session.connect()
        
        # Verify lip-sync configuration is set correctly
        assert session.lip_sync["sync_threshold_ms"] == 50
        assert session.lip_sync["accuracy_mode"] == "high"
        
        # Simulate audio data (0.1 second of audio at 24kHz, 16-bit PCM)
        audio_data = b"\x00" * 2400
        
        # Test that speak method accepts sync_threshold parameter
        await session.speak(audio_data, sample_rate=24000, sync_threshold_ms=50)
        
        # In production, this would verify actual audio-visual sync latency
        # Mock validates that the API is called with correct parameters
    
    @pytest.mark.asyncio
    async def test_get_stats(self):
        """Test getting video statistics"""
        session = AvatarSession(
            avatar_id="test-avatar",
            api_key="test-key",
            lip_sync={},
            eye_contact={},
            video_config={}
        )
        
        await session.connect()
        stats = await session.get_stats()
        
        assert "bitrate_kbps" in stats
        assert "fps" in stats
        assert "resolution" in stats
        assert stats["fps"] == 30
        assert stats["resolution"] == "720p"
    
    @pytest.mark.asyncio
    async def test_quality_adaptation(self):
        """Test animation quality adaptation (AC6)"""
        session = AvatarSession(
            avatar_id="test-avatar",
            api_key="test-key",
            lip_sync={},
            eye_contact={},
            video_config={}
        )
        
        await session.connect()
        
        # Test setting to low quality
        await session.set_animation_quality("low")
        assert session.animation_quality == "low"
        
        # Test restoring to high quality
        await session.set_animation_quality("high")
        assert session.animation_quality == "high"
    
    @pytest.mark.asyncio
    async def test_disconnect(self):
        """Test disconnecting avatar session"""
        session = AvatarSession(
            avatar_id="test-avatar",
            api_key="test-key",
            lip_sync={},
            eye_contact={},
            video_config={}
        )
        
        await session.connect()
        assert session.connected is True
        
        await session.disconnect()
        assert session.connected is False


class TestEmotionalExpressions:
    """Test emotional expression configuration and behavior"""
    
    def test_expression_presets_exist(self):
        """Test all required expression presets are defined (AC2)"""
        required_expressions = [
            EmotionalExpression.SUPPORTIVE,
            EmotionalExpression.CONCERNED,
            EmotionalExpression.ENCOURAGING,
            EmotionalExpression.NEUTRAL_LISTENING,
        ]
        
        for expression in required_expressions:
            assert expression in EXPRESSION_PRESETS
            preset = EXPRESSION_PRESETS[expression]
            assert "facial_config" in preset
            assert "body_language" in preset
            assert "animation" in preset
    
    def test_supportive_expression_config(self):
        """Test supportive expression has correct parameters"""
        preset = EXPRESSION_PRESETS[EmotionalExpression.SUPPORTIVE]
        
        # Gentle smile
        assert preset["facial_config"]["smile_intensity"] == 0.5
        # Warm, open eyes
        assert preset["facial_config"]["eye_openness"] == 0.75
        # Occasional nodding
        assert preset["animation"]["nodding_frequency"] == 0.15
    
    def test_concerned_expression_config(self):
        """Test concerned expression has correct parameters"""
        preset = EXPRESSION_PRESETS[EmotionalExpression.CONCERNED]
        
        # No smile
        assert preset["facial_config"]["smile_intensity"] == 0.0
        # Very attentive eyes
        assert preset["facial_config"]["eye_openness"] == 0.85
        # Furrowed brow
        assert preset["facial_config"]["eyebrow_position"] < 0
        # No nodding
        assert preset["animation"]["nodding_frequency"] == 0.0
    
    def test_encouraging_expression_config(self):
        """Test encouraging expression has correct parameters"""
        preset = EXPRESSION_PRESETS[EmotionalExpression.ENCOURAGING]
        
        # Bright smile
        assert preset["facial_config"]["smile_intensity"] == 0.8
        # Wide, engaged eyes
        assert preset["facial_config"]["eye_openness"] == 0.9
        # Frequent nodding
        assert preset["animation"]["nodding_frequency"] == 0.2
    
    def test_transition_config(self):
        """Test transition configuration (AC4)"""
        assert TRANSITION_CONFIG["duration_ms"] >= 300
        assert TRANSITION_CONFIG["duration_ms"] <= 500
        assert TRANSITION_CONFIG["easing"] == "ease-in-out"
        assert TRANSITION_CONFIG["min_interval_ms"] >= 3000


class TestEyeContact:
    """Test eye contact configuration"""
    
    def test_eye_contact_config(self):
        """Test eye contact configuration (AC5)"""
        assert EYE_CONTACT_CONFIG["primary_gaze"] == "camera"
        assert EYE_CONTACT_CONFIG["camera_focus_percentage"] == 80
        assert EYE_CONTACT_CONFIG["glance_away_angle"] > 0
        assert EYE_CONTACT_CONFIG["blink_rate_per_minute"] >= 15
        assert EYE_CONTACT_CONFIG["blink_rate_per_minute"] <= 20


class TestLipSync:
    """Test lip-sync configuration"""
    
    def test_lipsync_config(self):
        """Test lip-sync configuration (AC1)"""
        assert LIP_SYNC_CONFIG["accuracy_mode"] == "high"
        assert LIP_SYNC_CONFIG["sync_threshold_ms"] <= 50
        assert LIP_SYNC_CONFIG["phoneme_mapping"] == "english"
        assert LIP_SYNC_CONFIG["audio_sample_rate"] == 24000


class TestQualityAdaptation:
    """Test quality adaptation configuration"""
    
    def test_quality_adaptation_config(self):
        """Test quality adaptation settings (AC6)"""
        assert QUALITY_ADAPTATION_CONFIG["bitrate_threshold_low"] > 0
        assert QUALITY_ADAPTATION_CONFIG["fps_threshold_low"] > 0
        assert QUALITY_ADAPTATION_CONFIG["reduce_secondary_animations"] is True
        assert QUALITY_ADAPTATION_CONFIG["prioritize_lip_sync"] is True


class TestSentimentAnalysis:
    """Test sentiment-based expression triggering"""
    
    def test_crisis_keywords_defined(self):
        """Test crisis keywords are defined (AC3)"""
        assert len(CRISIS_KEYWORDS) > 0
        assert "suicide" in CRISIS_KEYWORDS
        assert "suicidal" in CRISIS_KEYWORDS
        assert "hurt myself" in CRISIS_KEYWORDS
    
    def test_positive_keywords_defined(self):
        """Test positive keywords are defined (AC3)"""
        assert len(POSITIVE_KEYWORDS) > 0
        assert "better" in POSITIVE_KEYWORDS
        assert "progress" in POSITIVE_KEYWORDS
        assert "proud" in POSITIVE_KEYWORDS


class TestVideoAgentExpressions:
    """Test video agent expression functionality"""
    
    @pytest.mark.asyncio
    async def test_agent_initializes_with_supportive_expression(self):
        """Test agent starts with supportive expression"""
        from video_agent import BeyondPresenceAvatarAgent
        
        with patch.dict(os.environ, {
            "ROOM_NAME": "test-room",
            "SESSION_ID": "test-session",
            "AVATAR_ID": "test-avatar",
            "BEY_AVATAR_API_KEY": "test-key",
            "SYSTEM_PROMPT": "Test prompt",
            "LIVEKIT_URL": "ws://test",
            "LIVEKIT_API_KEY": "test-key",
            "LIVEKIT_API_SECRET": "test-secret",
            "GOOGLE_API_KEY": "test-key",
        }):
            agent = BeyondPresenceAvatarAgent()
            assert agent.current_expression == EmotionalExpression.NEUTRAL_LISTENING
    
    @pytest.mark.asyncio
    async def test_set_expression_with_transition(self):
        """Test setting expression with smooth transition (AC4)"""
        from video_agent import BeyondPresenceAvatarAgent
        
        with patch.dict(os.environ, {
            "ROOM_NAME": "test-room",
            "SESSION_ID": "test-session",
            "AVATAR_ID": "test-avatar",
            "BEY_AVATAR_API_KEY": "test-key",
            "SYSTEM_PROMPT": "Test prompt",
            "LIVEKIT_URL": "ws://test",
            "LIVEKIT_API_KEY": "test-key",
            "LIVEKIT_API_SECRET": "test-secret",
            "GOOGLE_API_KEY": "test-key",
        }):
            agent = BeyondPresenceAvatarAgent()
            
            # Initialize avatar session
            agent.avatar_session = AvatarSession(
                avatar_id="test-avatar",
                api_key="test-key",
                lip_sync={},
                eye_contact={},
                video_config={}
            )
            await agent.avatar_session.connect()
            
            # Set expression
            start_time = time.time()
            await agent.set_expression(EmotionalExpression.ENCOURAGING)
            end_time = time.time()
            
            # Verify expression changed
            assert agent.current_expression == EmotionalExpression.ENCOURAGING
            
            # Verify transition duration
            transition_ms = (end_time - start_time) * 1000
            assert 300 <= transition_ms <= 600
    
    @pytest.mark.asyncio
    async def test_sentiment_triggers_concerned_expression(self):
        """Test crisis text triggers concerned expression (AC3)"""
        from video_agent import BeyondPresenceAvatarAgent
        
        with patch.dict(os.environ, {
            "ROOM_NAME": "test-room",
            "SESSION_ID": "test-session",
            "AVATAR_ID": "test-avatar",
            "BEY_AVATAR_API_KEY": "test-key",
            "SYSTEM_PROMPT": "Test prompt",
            "LIVEKIT_URL": "ws://test",
            "LIVEKIT_API_KEY": "test-key",
            "LIVEKIT_API_SECRET": "test-secret",
            "GOOGLE_API_KEY": "test-key",
        }):
            agent = BeyondPresenceAvatarAgent()
            
            # Initialize avatar session
            agent.avatar_session = AvatarSession(
                avatar_id="test-avatar",
                api_key="test-key",
                lip_sync={},
                eye_contact={},
                video_config={}
            )
            await agent.avatar_session.connect()
            
            # Test crisis text
            await agent.analyze_sentiment_and_express("I'm feeling suicidal")
            assert agent.current_expression == EmotionalExpression.CONCERNED
    
    @pytest.mark.asyncio
    async def test_sentiment_triggers_encouraging_expression(self):
        """Test positive text triggers encouraging expression (AC3)"""
        from video_agent import BeyondPresenceAvatarAgent
        
        with patch.dict(os.environ, {
            "ROOM_NAME": "test-room",
            "SESSION_ID": "test-session",
            "AVATAR_ID": "test-avatar",
            "BEY_AVATAR_API_KEY": "test-key",
            "SYSTEM_PROMPT": "Test prompt",
            "LIVEKIT_URL": "ws://test",
            "LIVEKIT_API_KEY": "test-key",
            "LIVEKIT_API_SECRET": "test-secret",
            "GOOGLE_API_KEY": "test-key",
        }):
            agent = BeyondPresenceAvatarAgent()
            
            # Initialize avatar session
            agent.avatar_session = AvatarSession(
                avatar_id="test-avatar",
                api_key="test-key",
                lip_sync={},
                eye_contact={},
                video_config={}
            )
            await agent.avatar_session.connect()
            
            # Wait for min interval to pass
            agent.last_expression_change = time.time() - 4.0
            
            # Test positive text
            await agent.analyze_sentiment_and_express("I'm feeling much better today!")
            assert agent.current_expression == EmotionalExpression.ENCOURAGING
    
    @pytest.mark.asyncio
    async def test_rapid_expression_changes_prevented(self):
        """Test that rapid expression changes are prevented"""
        from video_agent import BeyondPresenceAvatarAgent
        
        with patch.dict(os.environ, {
            "ROOM_NAME": "test-room",
            "SESSION_ID": "test-session",
            "AVATAR_ID": "test-avatar",
            "BEY_AVATAR_API_KEY": "test-key",
            "SYSTEM_PROMPT": "Test prompt",
            "LIVEKIT_URL": "ws://test",
            "LIVEKIT_API_KEY": "test-key",
            "LIVEKIT_API_SECRET": "test-secret",
            "GOOGLE_API_KEY": "test-key",
        }):
            agent = BeyondPresenceAvatarAgent()
            
            # Initialize avatar session
            agent.avatar_session = AvatarSession(
                avatar_id="test-avatar",
                api_key="test-key",
                lip_sync={},
                eye_contact={},
                video_config={}
            )
            await agent.avatar_session.connect()
            
            # Set first expression
            await agent.set_expression(EmotionalExpression.CONCERNED)
            assert agent.current_expression == EmotionalExpression.CONCERNED
            
            # Try to change immediately (should be skipped)
            await agent.set_expression(EmotionalExpression.ENCOURAGING)
            assert agent.current_expression == EmotionalExpression.CONCERNED  # Still concerned
    
    @pytest.mark.asyncio
    async def test_quality_monitoring_reduces_complexity(self):
        """Test quality monitoring reduces animation complexity (AC6)"""
        from video_agent import BeyondPresenceAvatarAgent
        
        with patch.dict(os.environ, {
            "ROOM_NAME": "test-room",
            "SESSION_ID": "test-session",
            "AVATAR_ID": "test-avatar",
            "BEY_AVATAR_API_KEY": "test-key",
            "SYSTEM_PROMPT": "Test prompt",
            "LIVEKIT_URL": "ws://test",
            "LIVEKIT_API_KEY": "test-key",
            "LIVEKIT_API_SECRET": "test-secret",
            "GOOGLE_API_KEY": "test-key",
        }):
            agent = BeyondPresenceAvatarAgent()
            
            # Initialize avatar session with low quality stats
            agent.avatar_session = AvatarSession(
                avatar_id="test-avatar",
                api_key="test-key",
                lip_sync={},
                eye_contact={},
                video_config={}
            )
            await agent.avatar_session.connect()
            
            # Mock low bandwidth stats
            async def mock_get_stats():
                return {
                    "bitrate_kbps": 400,  # Below 500 threshold
                    "fps": 18,            # Below 20 threshold
                    "resolution": "720p",
                }
            
            agent.avatar_session.get_stats = mock_get_stats
            
            # Run quality monitoring once
            # Create task and let it run once
            task = asyncio.create_task(agent.monitor_video_quality())
            await asyncio.sleep(0.1)
            task.cancel()
            
            # Quality should be reduced
            assert agent.avatar_session.animation_quality == "low"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
