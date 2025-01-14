from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Optional, Dict

from app.services.chatbot_services import handle_chatbot_request

router = APIRouter()

class ChatbotRequest(BaseModel):
    thread_id: str
    query: str
    match: Optional[Dict] = None

@router.post("/")
def chatbot_interaction(request: ChatbotRequest):
    try:
        # Access thread_id and query from the request body
        response = handle_chatbot_request(thread_id=request.thread_id, query=request.query, match=request.match)
        return {"response": response}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))