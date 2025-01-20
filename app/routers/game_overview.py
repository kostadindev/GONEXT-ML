from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Optional, Dict
from app.llm.llm_manager import LLMOptions
import pycountry

from app.services.game_overview_services import handle_game_overview_request

router = APIRouter()


class GameOverViewRequest(BaseModel):
    """
    Represents the structure of a chatbot interaction request.
    """
    model: str = LLMOptions.GEMINI_FLASH
    match: Optional[Dict] = None
    language: Optional[str] = "en"  # Added language field with a default value


@router.post("/")
def game_overview_interaction(request: GameOverViewRequest):
    try:
        # Access thread_id and query from the request body
        response = handle_game_overview_request(
            match=request.match,
            model_name=request.model,
            language=str(pycountry.languages.get(alpha_2=request.language)) or 'English'
        )
        return {"response": response}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))