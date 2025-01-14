from pydantic_settings import BaseSettings
from dotenv import load_dotenv

# Load .env file
load_dotenv()

class Settings(BaseSettings):
    openai_api_key: str
    langsmith_tracing: str = None  # Add this if needed
    langchain_api_key: str = None  # Add this if needed

    class Config:
        env_file = ".env"

settings = Settings()
