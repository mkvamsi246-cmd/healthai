import os
from pathlib import Path
from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import Field

# Get backend directory
BASE_DIR = Path(__file__).resolve().parent.parent

class Settings(BaseSettings):
    APP_NAME: str = "HealthInsight AI"
    APP_VERSION: str = "1.0.0"
    DEBUG: bool = False

    # Database Settings
    DATABASE_URL: str = "mysql+pymysql://root:password@localhost:3306/healthinsight_ai"
    DB_HOST: str = "localhost"
    DB_PORT: int = 3306
    DB_USER: str = "root"
    DB_PASSWORD: str = "password"
    DB_NAME: str = "healthinsight_ai"

    # JWT Settings
    SECRET_KEY: str = "your-very-secure-secret-key-change-this-in-production"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7

    # File Storage Settings
    UPLOAD_DIR: str = "uploads"
    REPORTS_DIR: str = "generated_reports"
    MAX_FILE_SIZE: int = 10485760  # 10 MB in bytes

    model_config = SettingsConfigDict(
        env_file=os.path.join(BASE_DIR, ".env"),
        env_file_encoding="utf-8",
        extra="ignore"
    )

    @property
    def upload_path(self) -> Path:
        path = BASE_DIR / self.UPLOAD_DIR
        path.mkdir(parents=True, exist_ok=True)
        return path

    @property
    def reports_path(self) -> Path:
        path = BASE_DIR / self.REPORTS_DIR
        path.mkdir(parents=True, exist_ok=True)
        return path

    @property
    def knowledge_path(self) -> Path:
        return BASE_DIR / "app" / "knowledge"

settings = Settings()
