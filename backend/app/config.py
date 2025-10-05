# app/config.py
from pydantic_settings import BaseSettings
from functools import lru_cache
from typing import Optional

class Settings(BaseSettings):
    """Application settings loaded from environment variables"""
    
    # App Info
    APP_NAME: str = "Crypto Portfolio Tracker"
    VERSION: str = "1.0.0"
    DEBUG: bool = True
    
    # Database
    DATABASE_URL: str = "postgresql://crypto_user:crypto_password@localhost:5432/crypto_portfolio"
    DATABASE_ECHO: bool = True  # SQL logging
    
    # Redis
    REDIS_URL: str = "redis://localhost:6379"
    
    # JWT Authentication
    JWT_SECRET_KEY: str = "your-super-secret-jwt-key-change-in-production"
    JWT_ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7
    
    # External APIs
    COINGECKO_API_KEY: Optional[str] = None
    COINGECKO_BASE_URL: str = "https://api.coingecko.com/api/v3"
    COINGECKO_RATE_LIMIT: int = 50  # requests per minute
    
    # AI Service (we'll add Gemini later)
    GEMINI_API_KEY: Optional[str] = None
    AI_INSIGHTS_ENABLED: bool = False
    
    # Background Tasks
    CELERY_BROKER_URL: str = "redis://localhost:6379/0"
    CELERY_RESULT_BACKEND: str = "redis://localhost:6379/0"
    
    # Observability
    METRICS_ENABLED: bool = True
    LOGGING_LEVEL: str = "INFO"
    
    # Security
    BCRYPT_ROUNDS: int = 12
    
    # Email (optional for now)
    SMTP_HOST: Optional[str] = None
    SMTP_PORT: int = 587
    SMTP_USER: Optional[str] = None
    SMTP_PASSWORD: Optional[str] = None
    EMAIL_FROM: str = "noreply@cryptoportfolio.com"

    # News API
    NEWSAPI_KEY: Optional[str] = None
    NEWSAPI_BASE_URL: str = "https://newsapi.org/v2"

# Gemini API (already exists but verify)
    GEMINI_API_KEY: Optional[str] = None
    
    class Config:
        env_file = ".env"
        case_sensitive = True

@lru_cache()
def get_settings() -> Settings:
    """Get cached settings instance"""
    return Settings()

# For easy access in other modules
settings = get_settings()