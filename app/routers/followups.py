from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import List, Dict, Optional
from app.services.followup_services import handle_followup_suggestions_request
from app.llm.llm_manager import LLMOptions
from app.models.response import ApiResponse, FollowupResponse, FollowupSuggestion
from app.utils.logger import get_logger
import uuid

router = APIRouter()
logger = get_logger("followups_router")

class FollowUpRequest(BaseModel):
    messages: List[Dict[str, str]]
    match: Optional[Dict] = None
    context: Optional[Dict] = None
    model: Optional[LLMOptions] = LLMOptions.GEMINI_FLASH
    language: Optional[str] = "en"

@router.post("/", response_model=ApiResponse)
def get_followup_suggestions(request: FollowUpRequest):
    """
    Get follow-up question suggestions based on the conversation history.
    
    Args:
        request: The request containing messages, optional match data, context, model choice and language
        
    Returns:
        ApiResponse: A response containing follow-up suggestions
    """
    try:
        logger.info(
            f"Received followup suggestions request",
            extra={"message_count": len(request.messages), "language": request.language}
        )
        
        # Get raw suggestions from service
        suggestions_list = handle_followup_suggestions_request(
            messages=request.messages,
            match=request.match,
            context=request.context,
            model_name=request.model,
            language=request.language
        )
        
        # Convert to FollowupSuggestion objects with IDs
        suggestions = [
            FollowupSuggestion(id=str(uuid.uuid4()), text=text) 
            for text in suggestions_list
        ]
        
        # Create response
        followup_response = FollowupResponse(suggestions=suggestions)
        
        logger.info(
            f"Successfully processed followup suggestions request",
            extra={"suggestion_count": len(suggestions)}
        )
        
        # Return wrapped in API response
        return ApiResponse(
            status="success",
            data=followup_response,
            message="Follow-up suggestions generated successfully"
        )
        
    except Exception as e:
        logger.error(f"Error generating follow-up suggestions: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail="Failed to generate suggestions")
