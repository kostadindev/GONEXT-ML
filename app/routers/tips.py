from fastapi import APIRouter, HTTPException, Depends
from typing import Dict, Any

from app.models.request import TipsRequest
from app.models.response import TipsResponse, ApiResponse
from app.services.tips_services import handle_tips_request
from app.utils.logger import get_logger
from app.utils.error_handler import ServiceUnavailableError, InvalidInputError
from app.dependencies import get_language_code, get_request_metadata

# Initialize router
router = APIRouter()

# Get module logger
logger = get_logger("tips_router")


@router.post("/", response_model=ApiResponse)
async def tips_interaction(
    request: TipsRequest,
    language_code: str = Depends(get_language_code),
    request_metadata: Dict[str, Any] = Depends(get_request_metadata)
):
    """
    Handles tips requests for game champion matchups or synergies.
    
    Args:
        request: The request payload containing champion information
        language_code: The normalized language code from the language dependency
        request_metadata: Request metadata for logging
        
    Returns:
        ApiResponse: A response containing the tips data
    """
    logger.info(
        f"Received tips request for game_id {request.game_id}",
        extra={**request_metadata, "player_id": request.player_id}
    )
    
    try:
        # Validate request data
        if not request.game_id:
            raise InvalidInputError(
                message="Game ID cannot be empty",
                detail={"game_id": request.game_id}
            )
            
        if not request.player_id:
            raise InvalidInputError(
                message="Player ID cannot be empty",
                detail={"player_id": request.player_id}
            )
        
        # Get tips from service layer
        response = handle_tips_request(
            game_id=request.game_id,
            player_id=request.player_id,
            language=language_code
        )
        
        logger.info(
            f"Successfully processed tips request for game_id {request.game_id}",
            extra={**request_metadata, "tips_count": len(response.tips)}
        )
        
        # Return successful response
        return ApiResponse(
            status="success",
            data=response,
            message="Tips retrieved successfully"
        )
        
    except InvalidInputError:
        # Re-raise invalid input errors to be handled by the global handler
        raise
    except Exception as e:
        logger.error(
            f"Unhandled error in tips_interaction: {str(e)}",
            exc_info=True,
            extra=request_metadata
        )
        raise ServiceUnavailableError(
            message="Failed to retrieve tips",
            detail={"error": str(e)}
        )