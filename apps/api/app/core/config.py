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

    # --- JWT Authentication ---
    JWT_SECRET_KEY: str = "yijian-ai-jwt-secret-key-2026-super-secure"
    JWT_ALGORITHM: str = "HS256"
    JWT_EXPIRE_HOURS: int = 24

    # --- Database ---
    DATABASE_URL: str = "sqlite:///./data/yijian.db"

    # --- CORS ---
    CORS_ORIGINS: list[str] = ["*"]

    # --- AI Model & Multi-Provider Image Generation ---
    AI_API_KEY: str = ""
    AI_API_BASE_URL: str = "https://api.openai.com/v1"
    AI_VISION_MODEL: str = "gpt-4o"
    AI_CHAT_MODEL: str = "gpt-4o-mini"

    # --- 国内主流 AI 视觉生图引擎配置 ---
    TRYON_DEFAULT_ENGINE: str = "seedream"        # 默认生图引擎: seedream (字节即梦大片) | wanx (阿里通义万相)
    VOLCENGINE_API_KEY: str = ""                  # 字节跳动火山方舟 API Key
    VOLCENGINE_BASE_URL: str = "https://ark.cn-beijing.volces.com/api/v3" # 火山方舟 API 地址
    VOLCENGINE_SEEDREAM_MODEL: str = "doubao-seedream-4-0-20260415" # 字节即梦模型版本

    DOMESTIC_TRYON_PROVIDER: str = "wanx"        # 国内引擎提供商: wanx (阿里通义万相) | doubao (字节火山方舟) | hunyuan (腾讯混元)
    DASHSCOPE_API_KEY: str = ""                  # 阿里百炼 API Key (留空时默认取 AI_API_KEY)
    HUNYUAN_API_KEY: str = ""                    # 腾讯混元 API Key

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
        env_file=(".env", "../.env", "../../.env", "../../../.env"),
        env_file_encoding="utf-8",
        case_sensitive=True,
        extra="ignore",
    )


settings = Settings()
