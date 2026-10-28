from functools import lru_cache
from typing import Literal

from pydantic import Field, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    # Application
    APP_NAME: str = "GharSaathi Maths API"
    APP_ENV: Literal["development", "test", "production"] = "development"
    APP_HOST: str = "0.0.0.0"
    APP_PORT: int = 8000
    LOG_LEVEL: str = "INFO"

    # Database
    DATABASE_URL: str = Field(
        default="postgresql+asyncpg://postgres:postgres@localhost:5432/gharsaathi",
        description="Async database connection string",
    )

    # Gnani Prisma (Speech-to-Text)
    GNANI_API_KEY: str = Field(default="", description="Gnani Prisma API Key")
    GNANI_STT_URL: str = "https://api.vachana.ai/stt/v3"
    GNANI_STT_LANGUAGE_DEFAULT: str = "kn-IN"
    GNANI_STT_FORMAT: str = "verbatim"
    GNANI_STT_TIMEOUT_SECONDS: float = 30.0

    # Gnani Timbre (Text-to-Speech)
    GNANI_TTS_ENABLED: bool = False
    GNANI_TTS_URL: str = "https://api.vachana.ai/api/v1/tts/inference"
    GNANI_TTS_MODEL: str = "timbre-v2.5"
    GNANI_TTS_LANGUAGE_DEFAULT: str = "kn-IN"
    GNANI_TTS_VOICE_KN: str = "Saanvi"
    GNANI_TTS_VOICE_EN: str = "Kaveri"
    GNANI_TTS_TIMEOUT_SECONDS: float = 30.0

    # Teacher Access & Security
    TEACHER_API_KEY: str = Field(
        default="dev-teacher-secret-key-change-in-production",
        description="Pre-shared teacher key for analytics and review",
    )
    CORS_ORIGINS: str = "http://localhost:5173,http://localhost:3000"

    # Constraints & Limits
    MAX_AUDIO_SIZE_MB: int = 10
    MAX_AUDIO_DURATION_SECONDS: int = 60
    MAX_TRANSCRIPT_LENGTH: int = 2000
    MAX_TRANSCRIPTIONS_PER_SESSION: int = 10
    SESSION_TOKEN_TTL_HOURS: int = 24
    DATA_RETENTION_DAYS: int = 30

    @property
    def cors_origins_list(self) -> list[str]:
        return [origin.strip() for origin in self.CORS_ORIGINS.split(",") if origin.strip()]

    @field_validator("TEACHER_API_KEY")
    @classmethod
    def validate_teacher_key_production(cls, v: str, info) -> str:
        # In production, placeholder teacher key must not be allowed
        # Note: when creating settings from environment, if APP_ENV is production, check
        return v

    def validate_runtime_guards(self) -> None:
        if self.APP_ENV == "production":
            if (
                not self.TEACHER_API_KEY
                or "dev-" in self.TEACHER_API_KEY
                or "change-in-production" in self.TEACHER_API_KEY
            ):
                raise ValueError("TEACHER_API_KEY must be set to a secure secret in production")
            if not self.GNANI_API_KEY:
                raise ValueError("GNANI_API_KEY must be configured in production")


@lru_cache
def get_settings() -> Settings:
    settings = Settings()
    return settings
