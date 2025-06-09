import os
import secrets
from typing import Optional

from pydantic_settings import BaseSettings

env_file_mappings = {
    "development": ".env.dev",
    "local": ".env.local",
    "production": ".env.prod",
}


class Settings(BaseSettings):
    """
    Application settings loaded from environment variables
    """

    API_V1_STR: str = "/api/v1"
    SECRET_KEY: str = secrets.token_urlsafe(32)
    ACCESS_TOKEN_EXPIRE_MINUTES: int = (
        60 * 24 * 8
    )  # 60 minutes * 24 hours * 8 days = 8 days
    PROJECT_NAME: str = "JourneyAI"
    ENVIRONMENT: str = "local"  # local, development, production

    # CORS
    BACKEND_CORS_ORIGINS: list[str] = []

    # MongoDB
    MONGODB_URL: str | None = None
    MONGODB_DB_NAME: str = "journeyai"

    # Qdrant
    QDRANT_URL: str | None = None
    QDRANT_API_KEY: str | None = None

    # Redis
    REDIS_HOST: str = "localhost"
    REDIS_PORT: int = 6379
    REDIS_DB: int = 0
    REDIS_PASSWORD: Optional[str] = None

    # Loki
    LOKI_URL: str | None = None

    # OpenAI
    OPENAI_API_KEY: str | None = None

    # Groq
    GROQ_API_KEY: str | None = None

    # Similarity Search Thresholds
    RELATED_ARTIFACTS_SCORE_THRESHOLD: float = 0.4
    RELATED_MESSAGES_SCORE_THRESHOLD: float = 0.4
    SEARCH_ARTIFACTS_SCORE_THRESHOLD: float = 0.5

    class Config:
        case_sensitive = True
        extra = "allow"
        env_file = env_file_mappings[os.getenv("ENVIRONMENT", "development")]


settings = Settings()
