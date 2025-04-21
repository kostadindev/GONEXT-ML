import pytest
from unittest.mock import patch, MagicMock
import uuid

def test_chatbot_endpoint_returns_200(client):
    """
    Test that the chatbot endpoint returns a 200 status code.
    """
    # Create a test request
    request_data = {
        "thread_id": str(uuid.uuid4()),
        "query": "What is League of Legends?",
        "model": "gemini-2.0-flash",
        "language": "en"
    }
    
    # Mock the response generator as a simple string yielder
    with patch("app.routers.chatbot.generate_chatbot_response_stream") as mock_generator:
        mock_generator.return_value = ["Test response"]
        
        # Send the request
        response = client.post("/chatbot/", json=request_data)
        
        # Verify response
        assert response.status_code == 200

def test_chatbot_validates_input(client):
    """
    Test that the chatbot endpoint validates input correctly.
    """
    # Create an invalid test request missing required fields
    request_data = {
        "query": "What is League of Legends?"
        # Missing thread_id
    }
    
    # Send the request
    response = client.post("/chatbot/", json=request_data)
    
    # Verify response
    assert response.status_code == 422  # Unprocessable Entity 

def test_chatbot_handles_custom_language(client):
    """
    Test that the chatbot endpoint correctly passes the language parameter
    from the request to the generate_chatbot_response_stream function.
    """
    # Create a test request with a specific language
    request_data = {
        "thread_id": str(uuid.uuid4()),
        "query": "What is League of Legends?",
        "model": "gemini-2.0-flash",
        "language": "fr"  # Request response in French
    }
    
    # Mock the response generator
    with patch("app.routers.chatbot.generate_chatbot_response_stream") as mock_generator:
        mock_generator.return_value = ["Réponse de test"]
        
        # Send the request
        response = client.post("/chatbot/", json=request_data)
        
        # Verify language was correctly passed to the generator
        mock_generator.assert_called_once()
        _, kwargs = mock_generator.call_args
        assert kwargs["language"] == "fr"
        
        # Verify response status
        assert response.status_code == 200 