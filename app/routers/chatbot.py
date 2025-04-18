from fastapi import APIRouter, HTTPException, Depends
from fastapi.responses import StreamingResponse
from typing import Optional, Dict, Generator, Any

from app.models.request import ChatbotRequest
from app.services.chatbot_services import handle_chatbot_request
from app.llm.llm_manager import LLMOptions
from app.dependencies import get_language_code, get_request_metadata
from app.utils.logger import get_logger
from app.utils.error_handler import ServiceUnavailableError, InvalidInputError

# Initialize router
router = APIRouter()

# Get module logger
logger = get_logger("chatbot_router")


def generate_chatbot_response_stream(
    thread_id: str, 
    query: str, 
    modelName: str, 
    match: Optional[Dict] = None, 
    language: str = "en",
    request_metadata: Optional[Dict[str, Any]] = None
) -> Generator[str, None, None]:
    """
    Generates a stream of chatbot responses for the given thread and query.

    Args:
        thread_id: The thread ID for the conversation
        query: The user query
        modelName: The model name to use
        match: Optional match data
        language: The desired response language
        request_metadata: Optional request metadata for logging

    Yields:
        Chunks of chatbot response content
    """
    request_id = request_metadata.get("request_id", "unknown") if request_metadata else "unknown"
    
    try:
        logger.info(
            f"Generating chatbot response stream for thread {thread_id}",
            extra={"request_id": request_id, "query": query, "model": modelName}
        )
        
        for chunk in handle_chatbot_request(
            thread_id=thread_id, 
            query=query, 
            modelName=modelName, 
            match=match or {}, 
            language=language
        ):
            yield chunk[1][0].content
            
    except Exception as e:
        logger.error(f"Error generating response stream: {str(e)}", exc_info=True, extra={"request_id": request_id})
        raise ServiceUnavailableError(
            message="Failed to generate chatbot response", 
            detail={"error": str(e)}
        )


@router.post("/")
async def chatbot_interaction(
    request: ChatbotRequest,
    language_code: str = Depends(get_language_code),
    request_metadata: Dict[str, Any] = Depends(get_request_metadata)
):
    """
    Handles chatbot interaction requests by streaming the response.

    Args:
        request: The request payload containing thread ID, query, and optional match data
        language_code: The normalized language code from the language dependency
        request_metadata: Request metadata for logging

    Returns:
        A streaming response with chatbot output
    """
    logger.info(
        f"Received chatbot interaction request for thread {request.thread_id}",
        extra={**request_metadata, "query_length": len(request.query)}
    )
    
    try:
        # Validate thread ID format
        if not request.thread_id or len(request.thread_id) < 3:
            raise InvalidInputError(
                message="Invalid thread ID format", 
                detail={"thread_id": request.thread_id}
            )
            
        # Validate query
        if not request.query or len(request.query.strip()) == 0:
            raise InvalidInputError(
                message="Query cannot be empty", 
                detail={"query": request.query}
            )
            
        # Generate response stream
        response_stream = generate_chatbot_response_stream(
            thread_id=request.thread_id,
            query=request.query,
            match=request.match,
            modelName=request.model,
            language=language_code,
            request_metadata=request_metadata
        )
        
        return StreamingResponse(
            response_stream, 
            media_type="text/event-stream"
        )
        
    except InvalidInputError:
        # Re-raise invalid input errors to be handled by the global handler
        raise
    except Exception as e:
        logger.error(
            f"Unhandled error in chatbot interaction: {str(e)}", 
            exc_info=True,
            extra=request_metadata
        )
        raise HTTPException(
            status_code=500, 
            detail={"message": "Internal Server Error", "error_type": type(e).__name__}
        )
