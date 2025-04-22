from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
from typing import Dict, Optional, Any
from app.services.game_overview_services import handle_game_overview_request, GameOverviewMLResponse
from app.llm.llm_manager import LLMOptions
from app.dependencies import get_language_code
from app.utils.logger import get_logger

# Initialize router
router = APIRouter()

# Get module logger
logger = get_logger("game_overview_router")

class GameOverviewRequest(BaseModel):
    """
    Request model for the game overview endpoint.
    """
    model: LLMOptions = LLMOptions.GEMINI_FLASH
    match: Dict[str, Any]
    language: Optional[str] = "en"

@router.post("/", response_model=GameOverviewMLResponse)
def get_game_overview(
    request: GameOverviewRequest,
    language_code: str = Depends(get_language_code)
):
    """
    Generate a comprehensive game overview and analysis.
    
    Args:
        request: The request containing match data, model choice and language
        language_code: The normalized language code from the language dependency
        
    Returns:
        GameOverviewMLResponse: A structured response with game analysis
    """
    try:
        # Use language from request if provided, otherwise use the language_code from dependency
        selected_language = request.language if request.language else language_code
        print(f"Selected language: {selected_language}")
        logger.info(
            f"Generating game overview",
            extra={"language": selected_language, "match_id": request.match.get("gameId", "unknown")}
        )
        
        return handle_game_overview_request(
            match=request.match,
            model_name=request.model,
            language=selected_language
        )
    except Exception as e:
        logger.error(f"Error generating game overview: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail="Failed to generate game overview")