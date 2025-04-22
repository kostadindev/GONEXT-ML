from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import List, Dict, Optional
from app.services.followup_services import handle_followup_suggestions_request
from app.llm.llm_manager import LLMOptions
from app.utils.logger import get_logger

router = APIRouter()
logger = get_logger("followups_router")

class FollowUpRequest(BaseModel):
    messages: List[Dict[str, str]]
    match: Optional[Dict] = None
    context: Optional[Dict] = None
    model: Optional[LLMOptions] = LLMOptions.GEMINI_FLASH
    language: Optional[str] = "en"

@router.post("/", response_model=List[str])
def get_followup_suggestions(request: FollowUpRequest):
    """
    Get follow-up question suggestions based on the conversation history.
    
    Args:
        request: The request containing messages, optional match data, context, model choice and language
        
    Returns:
        List[str]: A list of follow-up question suggestions
    """
    try:
        logger.info(
            f"Received followup suggestions request",
            extra={"message_count": len(request.messages), "language": request.language}
        )
        
        # Get suggestions from service
        suggestions = handle_followup_suggestions_request(
            messages=request.messages,
            match=request.match,
            context=request.context,
            model_name=request.model,
            language=request.language
        )
        
        logger.info(
            f"Successfully processed followup suggestions request",
            extra={"suggestion_count": len(suggestions)}
        )
        
        # Return the list of suggestions directly
        return suggestions
        
    except Exception as e:
        logger.error(f"Error generating follow-up suggestions: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail="Failed to generate suggestions")
