from typing import List, Dict, Any, Optional
from pydantic import BaseModel, Field
from langchain_core.prompts import PromptTemplate
from app.llm.llm import llm
from app.llm.llm_manager import LLMOptions
from app.utils.logger import get_logger
from app.utils.error_handler import ServiceUnavailableError

# Get module logger
logger = get_logger("game_overview_service")

class GameOverviewResponseData(BaseModel):
    """Model for the internal response data structure."""
    estimated_win_rate: float = Field(description="Estimated win rate as a decimal between 0 and 1")
    recommended_items: List[str] = Field(description="List of recommended items for the player")
    game_summary: str = Field(description="A summary of the game state and key moments")

class GameOverviewMLResponse(BaseModel):
    """Model for the game overview response from the ML service."""
    response: GameOverviewResponseData

# Define prompt template for game overview
template = (
    "You are a League of Legends expert analyzing a match.\n\n"
    "{match_block}"
    "Provide a comprehensive analysis of this game including:\n"
    "1. An estimated win rate (as a decimal between 0 and 1)\n"
    "2. A list of recommended items for the player\n"
    "3. A summary of the game state and key moments\n\n"
    "Make your analysis detailed but concise. All analysis should be in {language}.\n\n"
    "Format your response exactly according to this structure:\n"
    "- response.estimated_win_rate: A decimal number between 0 and 1\n"
    "- response.recommended_items: A list of item names as strings\n"
    "- response.game_summary: A concise overview of the match"
)

# Create prompt template
prompt = PromptTemplate.from_template(template)

def handle_game_overview_request(
    match: Dict[str, Any],
    model_name: LLMOptions = LLMOptions.GEMINI_FLASH,
    language: str = "en"
) -> GameOverviewMLResponse:
    """
    Generate a comprehensive game overview and analysis.
    
    Args:
        match: The match data to analyze
        model_name: The LLM model to use
        language: The language for the overview
        
    Returns:
        GameOverviewMLResponse containing the overview data matching the client's expected format
        
    Raises:
        ServiceUnavailableError: If there's an error generating the overview
    """
    try:
        # Log the request
        logger.info(
            f"Generating game overview",
            extra={"match_id": match.get("gameId", "unknown"), "language": language}
        )
        
        # Prepare match information
        match_block = f"Match information:\n{match}\n\n" if match else ""
        
        # Create LLM model with structured output
        model = llm.get(model_name).with_structured_output(GameOverviewMLResponse)
        
        # Chain prompt with model
        chain = prompt | model
        
        # Run chain with state
        output = chain.invoke({
            "match_block": match_block,
            "language": language
        })
        
        logger.info(
            f"Successfully generated game overview",
            extra={
                "match_id": match.get("gameId", "unknown"),
                "win_rate": output.response.estimated_win_rate,
                "items_count": len(output.response.recommended_items)
            }
        )
        
        return output
        
    except Exception as e:
        logger.error(
            f"Error in handle_game_overview_request: {e}",
            exc_info=True,
            extra={"match_id": match.get("gameId", "unknown")}
        )
        print(f"Error in handle_game_overview_request: {e}")
        raise
