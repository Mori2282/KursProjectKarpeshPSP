# config.py
from pathlib import Path
from pydantic_settings import BaseSettings

BASE_DIR = Path(__file__).resolve().parent

class Settings(BaseSettings):
    PROJECT_NAME: str = "Distributed Image Processing Pipeline"
    
    # Сетевые адреса хранилищ
    DATABASE_URL: str = "postgresql://mori:mori_password@localhost:5432/image_pipeline_db"
    REDIS_URL: str = "redis://localhost:6379/0"
    
    # Локальные директории
    UPLOAD_DIR: Path = BASE_DIR / "storage" / "uploads"
    RESULT_DIR: Path = BASE_DIR / "storage" / "results"
    
    API_HOST: str = "127.0.0.1"
    API_PORT: int = 8000

    class Config:
        case_sensitive = True

settings = Settings()
settings.UPLOAD_DIR.mkdir(parents=True, exist_ok=True)
settings.RESULT_DIR.mkdir(parents=True, exist_ok=True)
