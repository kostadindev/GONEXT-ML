import pytest
from unittest.mock import patch, MagicMock
import uuid
from app.models.response import GameOverviewResponse

def test_game_overview_endpoint_returns_200(client):
    """
    Test that the game overview endpoint returns a 200 status code.
    """
    # Create a test request
    request_data = {
        "game_id": str(uuid.uuid4()),
        "language": "en"
    }
    
    # Send the request
    response = client.post("/game_overview/", json=request_data)
    
    # Verify response
    assert response.status_code == 200
    assert response.json()["status"] == "success"

def test_game_overview_returns_api_response(client):
    """
    Test that the game overview endpoint returns a properly structured API response.
    """
    # Create a test request
    request_data = {
        "game_id": str(uuid.uuid4()),
        "language": "en"
    }
    
    # Send the request
    response = client.post("/game_overview/", json=request_data)
    
    # Verify response structure
    assert response.status_code == 200
    
    # Check response format
    response_data = response.json()
    assert "status" in response_data
    assert response_data["status"] == "success"
    assert "data" in response_data
    assert "game_id" in response_data["data"]
    assert "summary" in response_data["data"]
    assert "key_points" in response_data["data"]
    assert isinstance(response_data["data"]["key_points"], list)
    assert "performance" in response_data["data"]

def test_game_overview_validates_input(client):
    """
    Test that the game overview endpoint validates input correctly.
    """
    # Create an invalid test request missing required fields
    request_data = {
        # Missing game_id
        "language": "en"
    }
    
    # Send the request
    response = client.post("/game_overview/", json=request_data)
    
    # Verify response
    assert response.status_code == 422  # Unprocessable Entity 