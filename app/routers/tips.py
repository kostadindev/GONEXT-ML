from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from app.services.tips_services import handle_tips_request

# from app.services.chatbot_services import handle_chatbot_request

router = APIRouter()

class TipsRequest(BaseModel):
    my_champion: str
    other_champion: str
    tips_type: str

@router.post("/")
def tips_interaction(request: TipsRequest):
    try:
        # Access thread_id and query from the request body
        print("hitting here")
        response = handle_tips_request(my_champion=request.my_champion, other_champion=request.other_champion, tips_type=request.tips_type)
        return {"response": response}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))