from typing import List, Dict, Optional, Any
from uuid import uuid4
from langchain_core.prompts import PromptTemplate
from app.llm.llm import llm
from app.llm.llm_manager import LLMOptions
from app.utils.logger import get_logger
from app.utils.error_handler import ServiceUnavailableError
from app.models.response import FollowupResponse, FollowupSuggestion

# Get module logger
logger = get_logger("followup_service")

# Define prompt templates with language support
FOLLOWUP_TEMPLATE = (
    "You are an assistant helping League of Legends players with their questions about the game.\n"
    "The player has asked the following question in a conversation:\n\n"
    "Previous question: {previous_query}\n\n"
    "Based on this question, suggest 3 helpful follow-up questions the player might want to ask next. "
    "The follow-up questions should be related to League of Legends and relevant to their previous query. "
    "Provide questions that would help the player get more specific or detailed information.\n\n"
    "All suggestions should be in {language}.\n\n"
    "Remember that you are a League of Legends assistant, so keep the suggestions focused on game mechanics, "
    "champions, strategies, or other relevant topics."
)

# Create prompt template
followup_prompt = PromptTemplate.from_template(FOLLOWUP_TEMPLATE)

def handle_followup_suggestions_request(
    thread_id: str,
    previous_query: str,
    language: str = "en",
    model_name: str = LLMOptions.GEMINI_FLASH
) -> FollowupResponse:
    """
    Generate follow-up question suggestions based on a previous query.
    
    Args:
        thread_id: The conversation thread ID
        previous_query: The previous query from the user
        language: The language for the suggestions
        model_name: The LLM model to use
        
    Returns:
        FollowupResponse containing suggested follow-up questions
        
    Raises:
        ServiceUnavailableError: If there's an error generating suggestions
    """
    try:
        logger.info(
            f"Generating followup suggestions for thread {thread_id}",
            extra={"thread_id": thread_id, "query_length": len(previous_query)}
        )
        
        # Get LLM model
        model = llm.get(model_name)
        
        # Prepare input variables
        variables = {
            "previous_query": previous_query,
            "language": language
        }
        
        # Generate the prompt
        prompt = followup_prompt.format(**variables)
        
        # In a real implementation, we would call the model here
        # For now, we'll generate mock suggestions
        
        # Generate mock suggestions
        suggestions = [
            FollowupSuggestion(
                id=str(uuid4()),
                text=f"Follow-up question {i} about {previous_query[:20]}...",
                context={"type": "suggestion", "source": "generated"}
            )
            for i in range(1, 4)
        ]
        
        response = FollowupResponse(suggestions=suggestions)
        
        logger.info(
            f"Successfully generated {len(suggestions)} followup suggestions",
            extra={"thread_id": thread_id, "suggestion_count": len(suggestions)}
        )
        
        return response
        
    except Exception as e:
        logger.error(
            f"Error generating followup suggestions: {str(e)}",
            exc_info=True,
            extra={"thread_id": thread_id}
        )
        raise ServiceUnavailableError(
            message="Failed to generate follow-up suggestions",
            detail={"error": str(e), "thread_id": thread_id}
        )
