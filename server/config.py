from pydantic_settings import BaseSettings
from functools import lru_cache
from pathlib import Path


class Settings(BaseSettings):
    app_name: str = "Asclepius AI"
    debug: bool = True
    mongodb_url: str = ""
    database_name: str = "Asclepius"
    gemini_api_key: str = ""

    nurse_webhook_url: str = ""
    doctor_webhook_url: str = ""
    
    telegram_bot_token: str = ""
    telegram_nurse_chat_id: str = ""
    telegram_doctor_chat_id: str = ""

    risk_warning_threshold: int = 40
    risk_critical_threshold: int = 70
    sliding_window_minutes: int = 240

    class Config:
        env_file = Path(__file__).parent / ".env"
        extra = "ignore"


@lru_cache
def get_settings() -> Settings:
    return Settings()