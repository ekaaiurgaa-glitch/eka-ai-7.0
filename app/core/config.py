import os
from typing import List, Optional
from pydantic_settings import BaseSettings
from dotenv import load_dotenv

load_dotenv()


class Settings(BaseSettings):
    PROJECT_NAME: str = "EKA-AI Platform"
    API_V1_STR: str = "/api/v1"
    
    # Database - TDD Section 2.2: PostgreSQL 16 required in production
    ENVIRONMENT: str = os.getenv("ENVIRONMENT", "development")
    DATABASE_URL: str = os.getenv("DATABASE_URL", "sqlite:///./eka_ai.db")
    
    def __post_init__(self):
        if self.ENVIRONMENT == "production" and not self.DATABASE_URL.startswith("postgresql"):
            raise ValueError("TDD Violation: Production MUST use PostgreSQL 16")
    
    GEMINI_API_KEY: str = os.getenv("GEMINI_API_KEY", "")

    # JWT Auth - TDD Section 6.1: RS256, 15-minute expiry, 7-day refresh
    SECRET_KEY: str = os.getenv("SECRET_KEY")
    if not SECRET_KEY:
        raise ValueError("SECRET_KEY must be set in environment variables")
    ALGORITHM: str = os.getenv("ALGORITHM", "RS256")
    ACCESS_TOKEN_EXPIRE_MINUTES: int = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "15"))
    REFRESH_TOKEN_EXPIRE_DAYS: int = int(os.getenv("REFRESH_TOKEN_EXPIRE_DAYS", "7"))

    # Default Admin Credentials (override in production)
    ADMIN_USERNAME: str = os.getenv("ADMIN_USERNAME", "admin")
    ADMIN_PASSWORD: str = os.getenv("ADMIN_PASSWORD", "admin")

    # CORS
    ALLOWED_ORIGINS: List[str] = os.getenv("ALLOWED_ORIGINS", "http://localhost:3000,http://localhost:8080,*").split(",")

    # Redis (optional — graceful fallback if not set)
    REDIS_URL: Optional[str] = os.getenv("REDIS_URL")
    RATE_LIMIT_CHAT: str = os.getenv("RATE_LIMIT_CHAT", "20/minute")
    RATE_LIMIT_DEFAULT: str = os.getenv("RATE_LIMIT_DEFAULT", "60/minute")

    # Monitoring
    SENTRY_DSN: Optional[str] = os.getenv("SENTRY_DSN")
    LOG_LEVEL: str = os.getenv("LOG_LEVEL", "INFO")
    JSON_LOGS: bool = os.getenv("JSON_LOGS", "false").lower() == "true"
    
    # Tracing
    JAEGER_ENDPOINT: Optional[str] = os.getenv("JAEGER_ENDPOINT", "http://localhost:4317")

    model_config = {"case_sensitive": True}


settings = Settings()
