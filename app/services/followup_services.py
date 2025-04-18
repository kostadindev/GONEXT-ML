from typing import List, Dict, Optional
from pydantic import BaseModel, Field
from langchain_core.prompts import PromptTemplate
from app.llm.llm import llm
from app.llm.llm_manager import LLMOptions

class FollowUpSuggestions(BaseModel):
    suggestions: List[str] = Field(description="List of helpful follow-up questions.")

template = (
    "You are an assistant helping users continue their conversation in a helpful way.\n\n"
    "Conversation:\n{conversation}\n\n"
    "{context_block}"
    "{match_block}"
    "Based on this, suggest one or two helpful and relevant follow-up questions the user might ask next and can answer"
    "from the given context. Focus on information the human player might be interested in.\n"
    "Respond with only the questions in a Python list of strings. Do not suggest follow ups you cannot answer."
    "Make sure the questions are relevant and different from each other."
)

prompt = PromptTemplate.from_template(template)

def handle_followup_suggestions_request(
    messages: List[Dict[str, str]],
    match: Optional[Dict],
    context: Optional[Dict],
    model_name: LLMOptions
) -> List[str]:
    try:
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
        })

        return output.suggestions
    except Exception as e:
        print(f"Error in handle_followup_suggestions_request: {e}")
        raise
