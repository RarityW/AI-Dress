"""
Application configuration via Pydantic BaseSettings.
All settings are loaded from environment variables.
In development, a .env file in the project root is auto-loaded.
"""
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    # --- App ---
    PROJECT_NAME: str = "YIJIAN AI"
    APP_ENV: str = "development"
    LOG_LEVEL: str = "DEBUG"
    SECRET_KEY: str = "change-me-to-a-random-secret-key"
    API_V1_STR: str = "/api/v1"

    # --- Database ---
    DATABASE_URL: str = "sqlite:///./data/yijian.db"

    # --- CORS ---
    CORS_ORIGINS: list[str] = ["*"]

    # --- AI Model ---
    AI_API_KEY: str = ""
    AI_API_BASE_URL: str = "https://api.openai.com/v1"
    AI_VISION_MODEL: str = "gpt-4o"
    AI_CHAT_MODEL: str = "gpt-4o-mini"

    # --- Weather API ---
    WEATHER_API_KEY: str = ""
    WEATHER_API_BASE_URL: str = "https://api.seniverse.com/v3"

    # --- Recommendation Engine Weights (configurable, must sum to 1.0) ---
    WEIGHT_WEATHER: float = 0.35
    WEIGHT_STYLE: float = 0.25
    WEIGHT_SCENE: float = 0.20
    WEIGHT_COLOR: float = 0.15
    WEIGHT_PREFERENCE: float = 0.05

    # --- File Upload ---
    MAX_UPLOAD_SIZE_MB: int = 10
    ALLOWED_IMAGE_TYPES: list[str] = ["image/jpeg", "image/png", "image/webp"]
    UPLOAD_DIR: str = "uploads/clothing"

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=True,
        extra="ignore",
    )


settings = Settings()
