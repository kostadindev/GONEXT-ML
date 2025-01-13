from pydantic import BaseSettings

class Settings(BaseSettings):
    langchain_api_key: str
    database_url: str

    class Config:
        env_file = ".env"

settings = Settings()
