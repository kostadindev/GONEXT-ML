from typing import List, Dict, Optional
from pydantic import BaseModel, Field
from langchain_core.prompts import PromptTemplate
from app.llm.llm import llm
from app.llm.llm_manager import LLMOptions
from app.utils.logger import get_logger
from app.utils.error_handler import ServiceUnavailableError

# Get module logger
logger = get_logger("followup_service")

class FollowUpSuggestions(BaseModel):
    suggestions: List[str] = Field(description="List of helpful follow-up questions.")

template = (
    "You are an assistant helping users continue their conversation in a helpful way.\n\n"
    "Conversation:\n{conversation}\n\n"
    "{context_block}"
    "{match_block}"
    "Based on this, suggest one or two helpful and relevant follow-up questions the user might ask next and can answer "
    "from the given context. Focus on information the human player might be interested in.\n\n"
    "All suggested questions should be in {language}.\n\n"
    "Respond with only the questions in a Python list of strings. Do not suggest follow ups you cannot answer. "
    "Make sure the questions are relevant and different from each other. Keep the suggestions short and concise."
)

prompt = PromptTemplate.from_template(template)

def handle_followup_suggestions_request(
    messages: List[Dict[str, str]],
    match: Optional[Dict] = None,
    context: Optional[Dict] = None,
    model_name: LLMOptions = LLMOptions.GEMINI_FLASH,
    language: str = "en"
) -> List[str]:
    try:
        # Log request
        logger.info(
            f"Generating followup suggestions",
            extra={
                "has_messages": len(messages) > 0,
                "has_match": match is not None,
                "has_context": context is not None,
                "language": language
            }
        )
        
        # Format conversation
        conversation = "\n".join(
            [f"{msg['role'].capitalize()}: {msg['content']}" for msg in messages]
        )
        
        # Prepare variables
        context_block = f"Context:\n{context}\n\n" if context else ""
        match_block = f"Match info:\n{match}\n\n" if match else ""
        
        # Create LLM model with structured output
        model = llm.get(model_name).with_structured_output(FollowUpSuggestions)
        
        # Chain prompt with model
        chain = prompt | model
        
        # Run chain with state
        output = chain.invoke({
            "conversation": conversation,
            "context_block": context_block,
            "match_block": match_block,
            "language": language
        })
        
        logger.info(
            f"Successfully generated {len(output.suggestions)} followup suggestions",
            extra={"suggestion_count": len(output.suggestions), "language": language}
        )
        
        return output.suggestions
    except Exception as e:
        logger.error(
            f"Error in handle_followup_suggestions_request: {e}",
            exc_info=True
        )
        print(f"Error in handle_followup_suggestions_request: {e}")
        raise
