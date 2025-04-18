from typing import List, Dict, Any
from langchain_core.prompts import PromptTemplate
from app.llm.llm import llm
from app.llm.llm_manager import LLMOptions
from app.utils.logger import get_logger
from app.utils.error_handler import ServiceUnavailableError
from app.models.response import GameOverviewResponse

# Get module logger
logger = get_logger("game_overview_service")

# Define prompt templates with language support
OVERVIEW_TEMPLATE = (
    "You are a League of Legends expert analyzing a specific game.\n\n"
    "Game ID: {game_id}\n\n"
    "Provide a comprehensive analysis of this game including:\n"
    "1. A high-level summary of the game state and key moments\n"
    "2. Key strategic points that affected the outcome\n"
    "3. Performance analysis for each team\n\n"
    "Make your analysis detailed but concise. All analysis should be in {language}."
)

# Create prompt template
overview_prompt = PromptTemplate.from_template(OVERVIEW_TEMPLATE)

def handle_game_overview_request(
    game_id: str, 
    language: str = "en",
    model_name: str = LLMOptions.GEMINI_FLASH
) -> GameOverviewResponse:
    """
    Generate a comprehensive game overview and analysis.
    
    Args:
        game_id: The game identifier
        language: The language for the overview
        model_name: The LLM model to use
        
    Returns:
        GameOverviewResponse containing the overview data
        
    Raises:
        ServiceUnavailableError: If there's an error generating the overview
    """
    try:
        logger.info(
            f"Generating game overview for game {game_id}",
            extra={"game_id": game_id, "language": language}
        )
        
        # Get LLM model
        model = llm.get(model_name)
        
        # Prepare input variables
        variables = {
            "game_id": game_id,
            "language": language
        }
        
        # Generate the prompt
        prompt = overview_prompt.format(**variables)
        
        # In a real implementation, we would fetch game data and call the model
        # For now, we'll generate a mock overview
        
        # Generate mock data
        key_points = [
            "Early game objective control was decisive",
            "Mid-game teamfights determined momentum",
            "Late-game positioning was excellent"
        ]
        
        # Create response object
        response = GameOverviewResponse(
            game_id=game_id,
            summary="This is a sample game overview summary for demonstration purposes.",
            key_points=key_points,
            performance={
                "team1": {"kda": "15/10/23", "objectives": 4},
                "team2": {"kda": "10/15/18", "objectives": 2}
            }
        )
        
        logger.info(
            f"Successfully generated game overview for game {game_id}",
            extra={"game_id": game_id}
        )
        
        return response
        
    except Exception as e:
        logger.error(
            f"Error generating game overview: {str(e)}",
            exc_info=True,
            extra={"game_id": game_id}
        )
        raise ServiceUnavailableError(
            message="Failed to generate game overview",
            detail={"error": str(e), "game_id": game_id}
        )
