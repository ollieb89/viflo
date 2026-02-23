"""
Application settings.
"""
from typing import List
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Application configuration."""
    
    PROJECT_NAME: str = "FastAPI App"
    VERSION: str = "0.1.0"
    DESCRIPTION: str = "FastAPI application with SQLAlchemy"
    
    API_V1_STR: str = "/api/v1"
    
    # CORS
    ALLOWED_HOSTS: List[str] = ["*"]
    
    # Database
    DATABASE_URL: str = "postgresql://postgres:postgres@localhost:5432/app"
    
    # Security
    SECRET_KEY: str = "your-secret-key-change-in-production"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24  # 1 day
    
    class Config:
        env_file = ".env"
        case_sensitive = True


settings = Settings()
