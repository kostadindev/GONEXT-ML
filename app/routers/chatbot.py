from fastapi import APIRouter, HTTPException
from app.services.chatbot_services import handle_chatbot_request

router = APIRouter()

@router.post("/")
def chatbot_interaction(thread_id: str, query: str):
    try:
        response = handle_chatbot_request(thread_id=thread_id, query=query)
        return {"response": response}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
