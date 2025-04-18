from pydantic import BaseModel
from typing import List, Dict, Any, Optional

class ChatResponse(BaseModel):
    answer: str

class ApiResponse(BaseModel):
    """
    Standard API response model with status and data.
    """
    status: str
    data: Any
    message: Optional[str] = None

class FollowupSuggestion(BaseModel):
    """
    Model for a follow-up question suggestion.
    """
    id: str
    text: str
    context: Optional[Dict[str, Any]] = None

class FollowupResponse(BaseModel):
    """
    Response for follow-up suggestions.
    """
    suggestions: List[FollowupSuggestion]

class TipItem(BaseModel):
    """
    Single game tip item.
    """
    id: str
    title: str
    description: str
    category: str
    priority: int = 1

class TipsResponse(BaseModel):
    """
    Response containing game tips.
    """
    tips: List[TipItem]

class GameOverviewResponse(BaseModel):
    """
    Game overview response model.
    """
    game_id: str
    summary: str
    key_points: List[str]
    performance: Dict[str, Any]
