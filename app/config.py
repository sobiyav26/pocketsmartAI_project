from functools import lru_cache
from pathlib import Path
from pydantic import BaseModel
from dotenv import load_dotenv
import os

BASE_DIR = Path(__file__).resolve().parent.parent
load_dotenv(BASE_DIR / ".env")

class Settings(BaseModel):
    app_name: str = os.getenv("APP_NAME", "PocketSmart AI")
    secret_key: str = os.getenv("SECRET_KEY", "dev-secret-change-me")
    database_url: str = os.getenv("DATABASE_URL", "sqlite:///./pocketsmart.db")
    gemini_api_key: str = os.getenv("GEMINI_API_KEY", "")
    gemini_model: str = os.getenv("GEMINI_MODEL", "gemini-2.5-flash")
    gemini_api_base: str = os.getenv("GEMINI_API_BASE", "https://generativelanguage.googleapis.com/v1beta")
    access_token_expire_minutes: int = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "1440"))
    cors_origins: list[str] = [
        x.strip() for x in os.getenv(
            "CORS_ORIGINS", "http://127.0.0.1:8000,http://localhost:8000"
        ).split(",") if x.strip()
    ]
    use_mock_ai: bool = os.getenv("USE_MOCK_AI", "false").lower() == "true"
    max_image_mb: int = int(os.getenv("MAX_IMAGE_MB", "5"))
    upload_dir: Path = BASE_DIR / "uploads"

@lru_cache
def get_settings() -> Settings:
    settings = Settings()
    settings.upload_dir.mkdir(parents=True, exist_ok=True)
    return settings
