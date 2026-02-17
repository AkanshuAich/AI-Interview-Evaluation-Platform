"""
Configuration management for the AI Interview Platform.
Loads settings from environment variables with sensible defaults.
"""
from pydantic_settings import BaseSettings
from typing import List


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""
    
    # Database configuration
    DATABASE_URL: str = "postgresql+asyncpg://user:password@localhost:5432/ai_interview"
    
    # JWT configuration
    SECRET_KEY: str = "your-secret-key-change-in-production"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    
    # LLM API configuration
    LLM_PROVIDER: str = "openai"  # Options: "openai" or "gemini"
    LLM_API_KEY: str = ""
    LLM_API_URL: str = "https://api.openai.com/v1/chat/completions"
    LLM_MODEL: str = "gpt-4"
    
    # CORS configuration
    CORS_ORIGINS: List[str] = ["http://localhost:5173", "http://localhost:3000"]
    
    # Application settings
    PROJECT_NAME: str = "AI Interview Platform"
    VERSION: str = "1.0.0"
    
    class Config:
        env_file = ".env"
        case_sensitive = True


# Global settings instance
settings = Settings()
