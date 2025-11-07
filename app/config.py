
"""Configuration for CAIP loaded from environment variables.
Provides a Settings object with type hints for IDE support.
"""
from pydantic import BaseSettings
from pathlib import Path

class Settings(BaseSettings):
    DEBUG: bool = True
    DATABASE_URL: str = "sqlite+aiosqlite:///./caip_dev_async.db"
    REDIS_URL: str = "redis://localhost:6379/0"
    MEDIA_ROOT: str = "./media"
    MEDIA_URL: str = "/media/"

    class Config:
        env_file = ".env"

settings = Settings()

# Ensure media directory exists on startup
Path(settings.MEDIA_ROOT).mkdir(parents=True, exist_ok=True)
