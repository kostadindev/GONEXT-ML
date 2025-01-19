from fastapi import APIRouter, HTTPException
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
from typing import Optional, Dict, Generator

from app.services.chatbot_services import handle_chatbot_request
from app.llm.llm_manager import LLMOptions
import pycountry

router = APIRouter()


class ChatbotRequest(BaseModel):
    """
    Represents the structure of a chatbot interaction request.
    """
    thread_id: str
    query: str
    model: str = LLMOptions.GEMINI_FLASH
    match: Optional[Dict] = None
    language: Optional[str] = "en"  # Added language field with a default value


def generate_chatbot_response_stream(thread_id: str, query: str, modelName: LLMOptions, match: Optional[Dict], language: str) -> Generator[str, None, None]:
    """
    Generates a stream of chatbot responses for the given thread and query.

    Args:
        thread_id (str): The thread ID for the conversation.
        query (str): The user query.
        modelName (LLMOptions): The model name to use.
        match (Optional[Dict]): Optional match data.
        language (str): The desired response language.

    Yields:
        str: A chunk of chatbot response content.
    """
    try:
        for chunk in handle_chatbot_request(thread_id=thread_id, query=query, modelName=modelName, match=match or {}, language=language):
            yield chunk[1][0].content
    except Exception as e:
        # Log the exception for debugging purposes
        print(f"Error generating response stream: {e}")
        raise


@router.post("/")
def chatbot_interaction(request: ChatbotRequest):
    """
    Handles chatbot interaction requests by streaming the response.

    Args:
        request (ChatbotRequest): The request payload containing thread ID, query, language, and optional match data.

    Returns:
        StreamingResponse: A streaming response with chatbot output.
    """
    try:
        response_stream = generate_chatbot_response_stream(
            thread_id=request.thread_id,
            query=request.query,
            match=request.match,
            modelName=request.model,
            language=str(pycountry.languages.get(alpha_2=request.language)) or 'English'
        )
        return StreamingResponse(response_stream, media_type="text/event-stream")
    except Exception as e:
        # Log the exception for debugging purposes
        print(f"Error in chatbot interaction: {e}")
        raise HTTPException(status_code=500, detail="Internal Server Error")
