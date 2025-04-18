from fastapi import APIRouter, Depends, HTTPException
from typing import Dict, Any

from app.models.request import FollowupRequest
from app.models.response import FollowupResponse, ApiResponse
from app.services.followup_services import handle_followup_suggestions_request
from app.utils.logger import get_logger
from app.utils.error_handler import ServiceUnavailableError, InvalidInputError
from app.dependencies import get_language_code, get_request_metadata

# Initialize router
router = APIRouter()

# Get module logger
logger = get_logger("followups_router")


@router.post("/", response_model=ApiResponse)
async def get_followup_suggestions(
    request: FollowupRequest,
    language_code: str = Depends(get_language_code),
    request_metadata: Dict[str, Any] = Depends(get_request_metadata)
):
    """
    Generate follow-up question suggestions based on previous conversation.
    
    Args:
        request: The request containing the thread ID and previous query
        language_code: The normalized language code from the language dependency
        request_metadata: Request metadata for logging
        
    Returns:
        ApiResponse: A response containing the follow-up suggestions
    """
    logger.info(
        f"Received followup request for thread {request.thread_id}",
        extra={**request_metadata, "query_length": len(request.previous_query)}
    )
    
    try:
        # Validate thread ID
        if not request.thread_id:
            raise InvalidInputError(
                message="Thread ID cannot be empty",
                detail={"thread_id": request.thread_id}
            )
        
        # Validate previous query
        if not request.previous_query or len(request.previous_query.strip()) == 0:
            raise InvalidInputError(
                message="Previous query cannot be empty",
                detail={"previous_query": request.previous_query}
            )
        
        # Get suggestions from service layer
        suggestions = handle_followup_suggestions_request(
            thread_id=request.thread_id,
            previous_query=request.previous_query,
            language=language_code
        )
        
        logger.info(
            f"Generated {len(suggestions.suggestions)} followup suggestions for thread {request.thread_id}",
            extra={**request_metadata, "suggestion_count": len(suggestions.suggestions)}
        )
        
        # Return successful response
        return ApiResponse(
            status="success",
            data=suggestions,
            message="Follow-up suggestions generated successfully"
        )
        
    except InvalidInputError:
        # Re-raise invalid input errors to be handled by the global handler
        raise
    except Exception as e:
        logger.error(
            f"Unhandled error generating follow-up suggestions: {str(e)}",
            exc_info=True,
            extra=request_metadata
        )
        raise ServiceUnavailableError(
            message="Failed to generate follow-up suggestions",
            detail={"error": str(e)}
        )
