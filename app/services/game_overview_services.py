from typing import Sequence, List
from pydantic import BaseModel, Field
from langchain_core.prompts import PromptTemplate
from app.llm.llm import llm
from app.llm.llm_manager import LLMOptions

class GameOverview(BaseModel):
    """
    Estimated win rate, recommended items, and game summary
    """
    estimated_win_rate: float = Field(description="Estimated win rate of the matchup rounded to 2 decimal places")
    recommended_items: List[str] = Field(description="List of recommended item names for the specific match")
    game_summary: str = Field(description="Concise summary of the most important aspects of the specific match")


template = ("You are a League of Legends expert. Provide estimated win rate percentage (e.g xx.xx),"
            " recommended items, and a game summary"
            " for the specific match after analyzing it thoroughly."
                        "The summary should highlight the most important aspects for the upcoming match and should be "
            "intended for the searched player. Write the summary in {language}."
            "Give 6 good recommended items from League of Legends for the searched player's"
            " champion for the specific game. Write the item names in English"
            ""
            "Match: {match}")
prompt = PromptTemplate.from_template(template)


def handle_game_overview_request(match: dict, model_name: LLMOptions, language: str):
    try:
        model = llm.get(model_name).with_structured_output(GameOverview)
        chain = prompt | model
        state = {
            "match": match,
            "language": language
        }
        output = chain.invoke(state)
        return output
    except Exception as e:
        print(f"Error in handle_tips_request: {e}")
        return "An error occurred while processing your request. Please try again later."
