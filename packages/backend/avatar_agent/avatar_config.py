"""
Avatar Configuration for Beyond Presence Emotional Expressions.
Defines emotional presets, lip-sync settings, and quality adaptation configs.
"""

from enum import Enum
from typing import Dict, Any


class EmotionalExpression(Enum):
    """Counseling emotional expressions for avatar"""
    SUPPORTIVE = "supportive"
    CONCERNED = "concerned"
    ENCOURAGING = "encouraging"
    NEUTRAL_LISTENING = "neutral_listening"


# Emotional expression presets for Beyond Presence
EXPRESSION_PRESETS: Dict[EmotionalExpression, Dict[str, Any]] = {
    EmotionalExpression.SUPPORTIVE: {
        "name": "Supportive",
        "facial_config": {
            "smile_intensity": 0.5,  # Gentle smile
            "eye_openness": 0.75,    # Warm, open eyes
            "eyebrow_position": 0.2,  # Slightly raised (receptive)
            "head_tilt": 3,           # Slight tilt (3 degrees) - empathetic
        },
        "body_language": {
            "posture": "open",
            "lean_forward": 2,        # Leaning in slightly
            "hand_gestures": "minimal",
        },
        "animation": {
            "nodding_frequency": 0.15,  # Occasional nodding
            "micro_expressions": True,
        }
    },
    EmotionalExpression.CONCERNED: {
        "name": "Concerned",
        "facial_config": {
            "smile_intensity": 0.0,   # No smile
            "eye_openness": 0.85,     # Very attentive
            "eyebrow_position": -0.3,  # Slightly furrowed
            "head_tilt": 0,           # Straight, focused
        },
        "body_language": {
            "posture": "attentive",
            "lean_forward": 5,         # Leaning in more
            "hand_gestures": "minimal",
        },
        "animation": {
            "nodding_frequency": 0.0,   # No nodding
            "micro_expressions": True,
        }
    },
    EmotionalExpression.ENCOURAGING: {
        "name": "Encouraging",
        "facial_config": {
            "smile_intensity": 0.8,    # Bright smile
            "eye_openness": 0.9,       # Wide, engaged eyes
            "eyebrow_position": 0.4,   # Raised (positive)
            "head_tilt": 0,
        },
        "body_language": {
            "posture": "open",
            "lean_forward": 1,
            "hand_gestures": "moderate",  # More expressive
        },
        "animation": {
            "nodding_frequency": 0.2,   # Frequent nodding
            "micro_expressions": True,
        }
    },
    EmotionalExpression.NEUTRAL_LISTENING: {
        "name": "Neutral Listening",
        "facial_config": {
            "smile_intensity": 0.2,    # Slight smile
            "eye_openness": 0.7,
            "eyebrow_position": 0.0,   # Neutral
            "head_tilt": 0,
        },
        "body_language": {
            "posture": "neutral",
            "lean_forward": 0,
            "hand_gestures": "minimal",
        },
        "animation": {
            "nodding_frequency": 0.05,  # Rare nodding
            "micro_expressions": False,
        }
    },
}

# Eye contact configuration
EYE_CONTACT_CONFIG = {
    "primary_gaze": "camera",
    "camera_focus_percentage": 80,  # 80% looking at camera
    "glance_away_angle": 12,        # degrees
    "glance_duration": 1.5,         # seconds
    "blink_rate_per_minute": 18,
}

# Lip-sync configuration
LIP_SYNC_CONFIG = {
    "accuracy_mode": "high",        # high, medium, low
    "sync_threshold_ms": 50,       # Max 50ms latency
    "phoneme_mapping": "english",
    "audio_sample_rate": 24000,    # Hz
}

# Transition configuration
TRANSITION_CONFIG = {
    "duration_ms": 400,             # 400ms transitions
    "easing": "ease-in-out",
    "min_interval_ms": 3000,        # Min 3s between expression changes
}

# Quality adaptation
QUALITY_ADAPTATION_CONFIG = {
    "bitrate_threshold_low": 500,   # kbps
    "fps_threshold_low": 20,
    "reduce_secondary_animations": True,
    "prioritize_lip_sync": True,
}

# Crisis keywords for concerned expression
CRISIS_KEYWORDS = [
    "suicide", "suicidal", "kill myself", "end it all",
    "hurt myself", "self-harm", "don't want to live",
    "no reason to live", "better off dead", "want to die"
]

# Positive keywords for encouraging expression
POSITIVE_KEYWORDS = [
    "better", "improving", "good", "progress", "proud",
    "accomplished", "success", "happy", "grateful",
    "breakthrough", "healing", "growing"
]

# Avatar configurations by counselor category
AVATAR_CONFIG = {
    "Health": "health-counselor-avatar-001",
    "Career": "career-counselor-avatar-001",
    "Academic": "academic-counselor-avatar-001",
    "Financial Aid": "financial-counselor-avatar-001",
    "Social": "social-counselor-avatar-001",
    "Personal Development": "personal-dev-counselor-avatar-001",
    "General": "general-counselor-avatar-001",
}
