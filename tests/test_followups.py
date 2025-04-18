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
        "thread_id": str(uuid.uuid4()),
        "previous_query": "What are the best champions for top lane?",
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
        "thread_id": str(uuid.uuid4()),
        "previous_query": "What are the best champions for top lane?",
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
        "thread_id": str(uuid.uuid4()),
        # Missing previous_query
        "language": "en"
    }
    
    # Send the request
    response = client.post("/suggestions/", json=request_data)
    
    # Verify response
    assert response.status_code == 422  # Unprocessable Entity 