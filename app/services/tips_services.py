from langchain_openai import ChatOpenAI
from app.config import settings
from typing_extensions import Annotated
from typing import Sequence, Optional, Dict, List
from pydantic import BaseModel, Field
from langchain_core.prompts import PromptTemplate
from app.llm.llm import llm
from app.llm.llm_manager import LLMOptions
from app.utils.logger import get_logger
from app.utils.error_handler import ServiceUnavailableError
from app.models.response import TipItem, TipsResponse


class Tip(BaseModel):
    """Tip to play matchup or synergy"""
    title: str = Field(description="Title of the tip (e.g Trading, Farming, etc.)")
    description: str = Field(description="The concise tip to give to the user")


class Tips(BaseModel):
    """List of tips to play matchup or synergy"""
    tips: Annotated[Sequence[Tip], 'List of tips'] = Field(description="List of tips to play matchup or synergy")


# Get module logger
logger = get_logger("tips_service")

# Define prompt templates with language support
MATCHUP_TEMPLATE = (
    "You are a League of Legends expert. "
    "Analyze the game with ID {game_id} for player {player_id} and provide gameplay tips. "
    "Focus on champion matchups, item builds, map movements, and teamfight positioning. "
    "Categorize each tip with a meaningful title. "
    "All tips should be written in {language}."
)

# Create prompt template
matchup_prompt = PromptTemplate.from_template(MATCHUP_TEMPLATE)

def handle_tips_request(
    game_id: str, 
    player_id: str, 
    language: str = "en", 
    model_name: str = LLMOptions.GEMINI_FLASH
) -> TipsResponse:
    """
    Generate gameplay tips for a specific player in a game.
    
    Args:
        game_id: The game identifier
        player_id: The player's identifier
        language: The language for the tips
        model_name: The LLM model to use
        
    Returns:
        TipsResponse object containing the generated tips
        
    Raises:
        ServiceUnavailableError: If there's an error generating tips
    """
    try:
        logger.info(
            f"Generating tips for game {game_id}, player {player_id}",
            extra={"game_id": game_id, "player_id": player_id, "language": language}
        )
        
        # Get LLM model
        model = llm.get(model_name)
        
        # Prepare input variables
        variables = {
            "game_id": game_id,
            "player_id": player_id,
            "language": language
        }
        
        # Generate the prompt
        prompt = matchup_prompt.format(**variables)
        
        # In a real implementation, we would fetch game data here
        # For now, we'll generate mock tips
        
        # Call LLM and format response
        tips = [
            TipItem(
                id=f"tip-{i}",
                title=f"Tip {i}",
                description=f"This is a sample tip for game {game_id}",
                category="gameplay",
                priority=i
            ) 
            for i in range(1, 6)
        ]
        
        response = TipsResponse(tips=tips)
        
        logger.info(
            f"Successfully generated {len(tips)} tips for game {game_id}",
            extra={"game_id": game_id, "tips_count": len(tips)}
        )
        
        return response
    
    except Exception as e:
        logger.error(
            f"Error generating tips: {str(e)}",
            exc_info=True,
            extra={"game_id": game_id, "player_id": player_id}
        )
        raise ServiceUnavailableError(
            message="Failed to generate tips",
            detail={"error": str(e), "game_id": game_id}
        )
