from pydantic_settings import BaseSettings
from dotenv import load_dotenv
import os
from enum import Enum
from typing import Optional

# Load .env file
load_dotenv()

class Environment(str, Enum):
    DEVELOPMENT = "development"
    TESTING = "testing"
    STAGING = "staging"
    PRODUCTION = "production"

class Settings(BaseSettings):
    """
    Application settings class with environment-specific configuration.
    """
    # Environment settings
    APP_ENV: Environment = Environment.DEVELOPMENT
    DEBUG: bool = True
    
    # API Keys - allow both case formats from environment
    openai_api_key: str
    gemini_api_key: str
    
    # Observability settings
    langsmith_tracing: Optional[str] = None
    langchain_api_key: Optional[str] = None
    
    # Logging
    LOG_LEVEL: str = "INFO"
    LOG_FILE: Optional[str] = None
    
    # Performance
    MAX_WORKERS: int = 10
    TIMEOUT_SECONDS: int = 30
    
    class Config:
        env_file = ".env"
        case_sensitive = False  # Allow case-insensitive environment variable names

def get_settings():
    """
    Factory function to get settings for the current environment.
    
    Returns:
        Settings object configured for the current environment
    """
    env = os.getenv("APP_ENV", "development").lower()
    
    # Load base settings
    settings_obj = Settings()
    
    # Override settings based on environment
    if env == Environment.PRODUCTION:
        settings_obj.DEBUG = False
        settings_obj.LOG_LEVEL = "WARNING"
    elif env == Environment.TESTING:
        settings_obj.DEBUG = True
        settings_obj.LOG_LEVEL = "DEBUG"
    
    return settings_obj

# Create settings instance
settings = get_settings()
