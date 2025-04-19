from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import List, Dict, Optional
from app.services.followup_services import handle_followup_suggestions_request
from app.llm.llm_manager import LLMOptions

router = APIRouter()

class FollowUpRequest(BaseModel):
    messages: List[Dict[str, str]]
    match: Optional[Dict] = None
    context: Optional[Dict] = None
    model: Optional[LLMOptions] = LLMOptions.GEMINI_FLASH

@router.post("/", response_model=List[str])
def get_followup_suggestions(request: FollowUpRequest):
    try:
        return handle_followup_suggestions_request(
            messages=request.messages,
            match=request.match,
            context=request.context,
            model_name=request.model
        )
    except Exception as e:
        print(f"Error generating follow-up suggestions: {e}")
        raise HTTPException(status_code=500, detail="Failed to generate suggestions")
