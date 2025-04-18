from fastapi import APIRouter, Depends, HTTPException
from typing import Dict, Any

from app.models.request import GameOverviewRequest
from app.models.response import GameOverviewResponse, ApiResponse
from app.services.game_overview_services import handle_game_overview_request
from app.utils.logger import get_logger
from app.utils.error_handler import ServiceUnavailableError, InvalidInputError
from app.dependencies import get_language_code, get_request_metadata

# Initialize router
router = APIRouter()

# Get module logger
logger = get_logger("game_overview_router")


@router.post("/", response_model=ApiResponse)
async def game_overview_interaction(
    request: GameOverviewRequest,
    language_code: str = Depends(get_language_code),
    request_metadata: Dict[str, Any] = Depends(get_request_metadata)
):
    """
    Generate game overview and analysis for a specific game.
    
    Args:
        request: The request containing the game ID
        language_code: The normalized language code from the language dependency
        request_metadata: Request metadata for logging
        
    Returns:
        ApiResponse: A response containing the game overview data
    """
    logger.info(
        f"Received game overview request for game {request.game_id}",
        extra={**request_metadata, "game_id": request.game_id}
    )
    
    try:
        # Validate game ID
        if not request.game_id:
            raise InvalidInputError(
                message="Game ID cannot be empty",
                detail={"game_id": request.game_id}
            )
        
        # Get game overview from service layer
        overview = handle_game_overview_request(
            game_id=request.game_id,
            language=language_code
        )
        
        logger.info(
            f"Successfully generated game overview for game {request.game_id}",
            extra={**request_metadata}
        )
        
        # Return successful response
        return ApiResponse(
            status="success",
            data=overview,
            message="Game overview generated successfully"
        )
        
    except InvalidInputError:
        # Re-raise invalid input errors to be handled by the global handler
        raise
    except Exception as e:
        logger.error(
            f"Unhandled error generating game overview: {str(e)}",
            exc_info=True,
            extra=request_metadata
        )
        raise ServiceUnavailableError(
            message="Failed to generate game overview",
            detail={"error": str(e)}
        )