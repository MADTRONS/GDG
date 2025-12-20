from functools import lru_cache

from pydantic_settings import BaseSettings  # type: ignore[import-untyped]


class Settings(BaseSettings):
    class Config:
        env_file = '.env'
        case_sensitive = False

    # Database
    database_url: str = 'postgresql+asyncpg://counseling:devpassword@localhost:5432/counseling_platform'

    # JWT
    jwt_secret_key: str = 'your-secret-key-here-change-in-production'
    jwt_algorithm: str = 'HS256'
    jwt_expiration_minutes: int = 60 * 24  # 24 hours

    # CORS
    cors_origins: str = 'http://localhost:3000,http://localhost:3001'  # Comma-separated

    # External Services (placeholders)
    daily_api_key: str = ''
    livekit_api_key: str = ''
    livekit_api_secret: str = ''
    beyond_presence_api_key: str = ''
    deepgram_api_key: str = ''
    cartesia_api_key: str = ''
    google_api_key: str = ''
    openai_api_key: str = ''
    sentry_dsn: str = ''

@lru_cache
def get_settings() -> Settings:
    return Settings()