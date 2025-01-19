from langchain_openai import ChatOpenAI
from app.config import settings
from typing_extensions import Annotated
from typing import Sequence
from pydantic import BaseModel, Field
from langchain_core.prompts import PromptTemplate
from app.llm.llm import llm
from app.llm.llm_manager import LLMOptions


class Tip(BaseModel):
    """Tip to play matchup or synergy"""
    title: str = Field(description="Title of the tip (e.g Trading, Farming, etc.)")
    description: str = Field(description="The concise tip to give to the user")


class Tips(BaseModel):
    """List of tips to play matchup or synergy"""
    tips: Annotated[Sequence[Tip], 'List of tips'] = Field(description="List of tips to play matchup or synergy")


template = ("You are a League of Legends expert. Provide tips on the {tips_type} between"
            " me as {my_champion} and {other_champion}. Provide meaningful titles and specific descriptions."
            " All tips should be written in {language}.")
prompt = PromptTemplate.from_template(template)


def handle_tips_request(tips_type: str, my_champion: str, other_champion: str, modelName: LLMOptions, language: str):
    try:
        model = llm.get(modelName).with_structured_output(Tips)
        tips_chain = prompt | model
        state = {
            "tips_type": tips_type,
            "my_champion": my_champion,
            "other_champion": other_champion,
            "language": language
        }
        output = tips_chain.invoke(state)
        return output
    except Exception as e:
        print(f"Error in handle_tips_request: {e}")
        return "An error occurred while processing your request. Please try again later."
