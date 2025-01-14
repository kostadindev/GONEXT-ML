from fastapi import Depends
from app.config import settings

def get_langchain_api_key():
    return settings.langchain_api_key
