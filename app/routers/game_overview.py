from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Dict, Optional, Any
from app.services.game_overview_services import handle_game_overview_request, GameOverviewMLResponse
from app.llm.llm_manager import LLMOptions

# Initialize router
router = APIRouter()

class GameOverviewRequest(BaseModel):
    """
    Request model for the game overview endpoint.
    """
    model: LLMOptions = LLMOptions.GEMINI_FLASH
    match: Dict[str, Any]
    language: str = "en"

@router.post("/", response_model=GameOverviewMLResponse)
def get_game_overview(request: GameOverviewRequest):
    """
    Generate a comprehensive game overview and analysis.
    
    Args:
        request: The request containing match data, model choice and language
        
    Returns:
        GameOverviewMLResponse: A structured response with game analysis
    """
    try:
        return handle_game_overview_request(
            match=request.match,
            model_name=request.model,
            language=request.language
        )
    except Exception as e:
        print(f"Error generating game overview: {e}")
        raise HTTPException(status_code=500, detail="Failed to generate game overview")