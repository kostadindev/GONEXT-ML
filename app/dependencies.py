from fastapi import Depends, Request, Header
from app.config import settings
from app.utils.logger import get_logger
from typing import Optional, Dict, Any
from app.llm.llm import llm
from app.llm.llm_manager import LLMOptions
import pycountry

# Get logger for dependencies
logger = get_logger("dependencies")

def get_langchain_api_key():
    """
    Dependency to provide the Langchain API key.
    """
    return settings.langchain_api_key

def get_model(model_name: Optional[str] = None):
    """
    Dependency to provide an LLM model instance.
    
    Args:
        model_name: Optional model name to use
    
    Returns:
        An instance of the requested LLM model
    """
    model = model_name or LLMOptions.GEMINI_FLASH
    logger.debug(f"Creating model instance: {model}")
    return llm.get(model)

def get_language_code(language: Optional[str] = "en") -> str:
    """
    Dependency to validate and normalize language codes.
    
    Args:
        language: ISO language code or language name
        
    Returns:
        Normalized language code or "en" for English if invalid
    """
    try:
        # Try direct lookup
        lang = pycountry.languages.get(alpha_2=language)
        if lang:
            return language.lower()
            
        # Try name-based lookup
        candidates = [l for l in pycountry.languages if getattr(l, 'name', '').lower() == language.lower()]
        if candidates:
            return candidates[0].alpha_2.lower()
            
        # Default to English
        logger.warning(f"Invalid language code: {language}, defaulting to 'en'")
        return "en"
    except Exception as e:
        logger.error(f"Error processing language code: {e}")
        return "en"

def get_request_metadata(
    request: Request,
    user_agent: Optional[str] = Header(None),
    x_request_id: Optional[str] = Header(None)
) -> Dict[str, Any]:
    """
    Dependency to provide request metadata for logging and tracking.
    
    Args:
        request: The FastAPI request object
        user_agent: The User-Agent header value
        x_request_id: The X-Request-ID header value
        
    Returns:
        Dictionary with request metadata
    """
    client_host = request.client.host if request.client else "unknown"
    
    return {
        "request_id": x_request_id,
        "path": request.url.path,
        "method": request.method,
        "client_ip": client_host,
        "user_agent": user_agent
    }
