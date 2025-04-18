import pytest
from fastapi.testclient import TestClient
import os
import dotenv
from app.main import create_app
from app.llm.llm import llm
from unittest.mock import patch, MagicMock

# Load test environment variables
dotenv.load_dotenv(".env.test", override=True)

# Set environment to testing
os.environ["APP_ENV"] = "testing"

# Mock the LLM singleton to avoid calling real API endpoints
@pytest.fixture(autouse=True)
def mock_llm():
    """
    Fixture that provides a mock LLM for testing.
    
    This fixture is automatically used in all tests to mock the LLM.
    """
    mock_llm_instance = MagicMock()
    mock_llm_instance.get.return_value = MagicMock()
    mock_llm_instance.get.return_value.invoke.return_value = "This is a mock response from the LLM."
    
    with patch("app.llm.llm_manager.LLM._instance", mock_llm_instance):
        with patch("app.llm.llm.llm", mock_llm_instance):
            yield mock_llm_instance

@pytest.fixture
def app():
    """
    Fixture that creates an app instance for testing.
    """
    return create_app()

@pytest.fixture
def client(app):
    """
    Fixture that creates a test client.
    """
    return TestClient(app)

@pytest.fixture
def auth_headers():
    """
    Fixture that provides mock authentication headers for testing protected endpoints.
    """
    return {"Authorization": "Bearer test_token"} 