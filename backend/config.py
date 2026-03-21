from pydantic_settings import BaseSettings
from functools import lru_cache
import os
from pathlib import Path

# Get the backend directory (where this file is located)
BACKEND_DIR = Path(__file__).parent


class Settings(BaseSettings):
    app_name: str = "Asclepius AI"
    debug: bool = True
    database_url: str = f"sqlite+aiosqlite:///{BACKEND_DIR}/asclepius.db"
    gemini_api_key: str = ""

    nurse_webhook_url: str = ""
    doctor_webhook_url: str = ""

    risk_warning_threshold: int = 40
    risk_critical_threshold: int = 70
    sliding_window_minutes: int = 240

    class Config:
        env_file = ".env"


@lru_cache
def get_settings() -> Settings:
    return Settings()