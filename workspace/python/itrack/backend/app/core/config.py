from pydantic_settings import BaseSettings
from pydantic import model_validator
from functools import lru_cache

_EXAMPLE_KEY = "your-secret-key-change-this-in-production-min-32-chars"


class Settings(BaseSettings):
    """Application settings with environment variable support."""

    # MongoDB
    MONGODB_URL: str = "mongodb://localhost:27017"
    MONGODB_DB_NAME: str = "itrack_db"

    # Security — no default; must be supplied via environment
    SECRET_KEY: str
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30

    # CORS
    FRONTEND_URL: str = "http://localhost:3000"

    # Environment
    ENVIRONMENT: str = "development"
    # Redis (optional) - used for rate limiter and token blocklist persistence
    REDIS_URL: str | None = None

    # Sentry (optional) for error reporting
    SENTRY_DSN: str | None = None

    @model_validator(mode="after")
    def validate_secret_key(self):
        if self.SECRET_KEY == _EXAMPLE_KEY:
            raise ValueError(
                "SECRET_KEY is still set to the example placeholder. "
                "Set a random 32+ character string in your environment."
            )
        if len(self.SECRET_KEY) < 32:
            raise ValueError("SECRET_KEY must be at least 32 characters long.")
        return self

    class Config:
        env_file = ".env"
        case_sensitive = True
        extra = "ignore"


@lru_cache()
def get_settings() -> Settings:
    return Settings()
