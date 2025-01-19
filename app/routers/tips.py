import pycountry
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from app.services.tips_services import handle_tips_request
from app.llm.llm_manager import LLMOptions

# from app.services.chatbot_services import handle_chatbot_request

router = APIRouter()

class TipsRequest(BaseModel):
    my_champion: str
    other_champion: str
    tips_type: str
    model: str = LLMOptions.GEMINI_FLASH
    language: str = "en"

@router.post("/")
def tips_interaction(request: TipsRequest):
    try:
        # Access thread_id and query from the request body
        print("hitting here", request.language, request.model)
        response = handle_tips_request(
            my_champion=request.my_champion,
            other_champion=request.other_champion,
            tips_type=request.tips_type,
            modelName=request.model,
            language=str(pycountry.languages.get(alpha_2=request.language)) or 'English'
        )
        return {"response": response}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))