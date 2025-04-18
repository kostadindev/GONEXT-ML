import pytest
from unittest.mock import patch, MagicMock
import uuid
from app.models.response import TipsResponse, TipItem
from app.utils.error_handler import ServiceUnavailableError

def test_tips_endpoint_returns_200(client):
    """
    Test that the tips endpoint returns a 200 status code.
    """
    # Create a test request
    request_data = {
        "game_id": str(uuid.uuid4()),
        "player_id": "player123",
        "language": "en"
    }
    
    # Send the request
    response = client.post("/tips/", json=request_data)
    
    # Verify basic response structure
    assert response.status_code == 200
    assert response.json()["status"] == "success"
    assert len(response.json()["data"]["tips"]) > 0

def test_tips_returns_api_response(client):
    """
    Test that the tips endpoint returns a properly structured API response.
    """
    # Create a test request
    request_data = {
        "game_id": str(uuid.uuid4()),
        "player_id": "player123",
        "language": "en"
    }
    
    # Send the request
    response = client.post("/tips/", json=request_data)
    
    # Verify response structure
    assert response.status_code == 200
    
    # Check response format
    response_data = response.json()
    assert "status" in response_data
    assert response_data["status"] == "success"
    assert "data" in response_data
    assert "tips" in response_data["data"]
    assert isinstance(response_data["data"]["tips"], list)
    
    # Check a tip's structure
    if response_data["data"]["tips"]:
        tip = response_data["data"]["tips"][0]
        assert "id" in tip
        assert "title" in tip
        assert "description" in tip

def test_tips_validates_input(client):
    """
    Test that the tips endpoint validates input correctly.
    """
    # Create an invalid test request missing required fields
    request_data = {
        "game_id": str(uuid.uuid4()),
        # Missing player_id
        "language": "en"
    }
    
    # Send the request
    response = client.post("/tips/", json=request_data)
    
    # Verify response
    assert response.status_code == 422  # Unprocessable Entity 