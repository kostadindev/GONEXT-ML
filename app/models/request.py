from pydantic import BaseModel
from typing import Dict, Optional, List

class ChatRequest(BaseModel):
    query: str

class ChatbotRequest(BaseModel):
    """
    Represents the structure of a chatbot interaction request.
    """
    thread_id: str
    query: str
    model: str
    match: Optional[Dict] = None
    language: Optional[str] = "en"

class TipsRequest(BaseModel):
    """
    Represents a request for game tips.
    """
    game_id: str
    player_id: str
    language: Optional[str] = "en"

class FollowupRequest(BaseModel):
    """
    Represents a request for suggested follow-up questions.
    """
    thread_id: str
    previous_query: str
    language: Optional[str] = "en"

class GameOverviewRequest(BaseModel):
    """
    Represents a request for game overview data.
    """
    game_id: str
    language: Optional[str] = "en"
