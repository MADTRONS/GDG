from functools import lru_cache

from pydantic_settings import BaseSettings  # type: ignore[import-untyped]


class Settings(BaseSettings):
    class Config:
        env_file = '.env'
        case_sensitive = False

    # Database
    database_url: str = 'postgresql+psycopg://counseling:devpassword@localhost:5432/counseling_platform'

    # JWT
    jwt_secret_key: str = 'your-secret-key-here-change-in-production'
    jwt_algorithm: str = 'HS256'
    jwt_expiration_minutes: int = 60 * 24  # 24 hours

    # Environment
    environment: str = 'development'  # 'development', 'test', 'production'

    # CORS
    cors_origins: str = 'http://localhost:3000,http://localhost:3001'  # Comma-separated

    # External Services (placeholders)
    daily_api_key: str = ''
    livekit_url: str = ''
    livekit_api_key: str = ''
    livekit_api_secret: str = ''
    bey_avatar_id: str = ''
    bey_avatar_api_key: str = ''  # Beyond Presence API key
    deepgram_api_key: str = ''
    cartesia_api_key: str = ''
    google_api_key: str = ''
    google_tts_api_key: str = ''  # For Text-to-Speech
    openai_api_key: str = ''
    sentry_dsn: str = ''

@lru_cache
def get_settings() -> Settings:
    return Settings()
