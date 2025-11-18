from pydantic_settings import BaseSettings
from typing import Optional


class Settings(BaseSettings):
    # Database
    DATABASE_URL: str = "sqlite+aiosqlite:///./virtual_economy.db"

    # Redis
    REDIS_HOST: str = "localhost"
    REDIS_PORT: int = 6379
    REDIS_PASSWORD: Optional[str] = None

    # Celery
    CELERY_BROKER_URL: str = "redis://localhost:6379/0"
    CELERY_RESULT_BACKEND: str = "redis://localhost:6379/0"

    # Application
    APP_VERSION: str = "1.0.0"
    DEBUG: bool = True

    # Rate Limiting
    RATE_LIMITING_ENABLED: bool = True

    class Config:
        env_file = ".env"


settings = Settings()