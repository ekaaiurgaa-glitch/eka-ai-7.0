import os
from pydantic_settings import BaseSettings
from dotenv import load_dotenv

load_dotenv()

class Settings(BaseSettings):
    PROJECT_NAME: str = "EKA-AI Platform"
    API_V1_STR: str = "/api/v1"
    DATABASE_URL: str = os.getenv("DATABASE_URL", "sqlite:///./eka_ai.db")
    GEMINI_API_KEY: str = os.getenv("GEMINI_API_KEY")

    model_config = {"case_sensitive": True}


settings = Settings()
