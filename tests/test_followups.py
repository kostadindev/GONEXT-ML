import pytest
from unittest.mock import patch, MagicMock
import uuid
from app.models.response import FollowupResponse, FollowupSuggestion

def test_followup_endpoint_returns_200(client):
    """
    Test that the followup suggestions endpoint returns a 200 status code.
    """
    # Create a test request
    request_data = {
        "messages": [
            {"role": "user", "content": "What are the best champions for top lane?"}
        ],
        "language": "en"
    }
    
    # Send the request
    response = client.post("/suggestions/", json=request_data)
    
    # Verify response
    assert response.status_code == 200
    assert response.json()["status"] == "success"

def test_followup_returns_api_response(client):
    """
    Test that the followup endpoint returns a properly structured API response.
    """
    # Create a test request
    request_data = {
        "messages": [
            {"role": "user", "content": "What are the best champions for top lane?"}
        ],
        "language": "en"
    }
    
    # Send the request
    response = client.post("/suggestions/", json=request_data)
    
    # Verify response structure
    assert response.status_code == 200
    
    # Check response format
    response_data = response.json()
    assert "status" in response_data
    assert response_data["status"] == "success"
    assert "data" in response_data
    assert "suggestions" in response_data["data"]
    assert isinstance(response_data["data"]["suggestions"], list)
    
    # Check a suggestion's structure
    if response_data["data"]["suggestions"]:
        suggestion = response_data["data"]["suggestions"][0]
        assert "id" in suggestion
        assert "text" in suggestion

def test_followup_validates_input(client):
    """
    Test that the followup suggestions endpoint validates input correctly.
    """
    # Create an invalid test request missing required fields
    request_data = {
        # Missing messages
        "language": "en"
    }
    
    # Send the request
    response = client.post("/suggestions/", json=request_data)
    
    # Verify response
    assert response.status_code == 422  # Unprocessable Entity

def test_followup_uses_specified_language(client):
    """
    Test that the followup endpoint uses the specified language.
    """
    # Create a test request with French language
    request_data = {
        "messages": [
            {"role": "user", "content": "What are the best champions for top lane?"}
        ],
        "language": "fr"  # Request suggestions in French
    }
    
    # Mock the followup service to verify language is passed
    with patch("app.services.followup_services.handle_followup_suggestions_request") as mock_service:
        mock_service.return_value = ["Suggestion 1", "Suggestion 2"]
        
        # Send the request
        response = client.post("/suggestions/", json=request_data)
        
        # Verify language was passed correctly
        _, kwargs = mock_service.call_args
        assert kwargs["language"] == "fr"
        
        # Verify response status
        assert response.status_code == 200 