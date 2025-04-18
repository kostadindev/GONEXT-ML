# **GONEXT** - League of Legends Assistant API

This is the ML server for **GONEXT** - a GenAI-powered assistant tailored for League of Legends players.

**GONEXT** delivers real-time and personalized strategies, matchups, synergies, and builds. By harnessing the Riot API, **GONEXT** retrieves live game data—covering both allied and enemy players—and employs large language models to offer context-specific guidance for every match.

## Features

- **Chatbot Interface**: Conversational AI assistant for League of Legends players
- **Game Tips**: Personalized gameplay tips based on match context
- **Follow-up Suggestions**: Dynamic follow-up questions based on conversation context
- **Game Overviews**: Comprehensive game analysis and summaries

## Architecture

The application follows a clean architecture with the following components:

- **API Layer**: FastAPI endpoints that handle HTTP requests and responses
- **Services Layer**: Business logic and domain services
- **Models**: Data structures and schemas
- **LLM Integration**: Abstraction for working with multiple language models

## Getting Started

### Prerequisites

- Python 3.9+
- Poetry (recommended) or pip

### Installation

1. Clone the repository:
   ```
   git clone https://github.com/yourusername/gonext-ml.git
   cd gonext-ml
   ```

2. Create a virtual environment:
   ```
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. Install dependencies:
   ```
   pip install -r requirements.txt
   ```

4. Set up environment variables:
   ```
   cp .env.sample .env
   ```
   
   Edit `.env` to include your API keys:
   ```
   openai_api_key=your_openai_key_here
   gemini_api_key=your_gemini_key_here
   ```

### Running the Application

Start the development server:

```
uvicorn app.main:app --reload
```

The API will be available at http://localhost:8000

### API Documentation

Once the server is running, access the interactive API documentation at:

- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

## Testing

Run tests using pytest:

```
pytest
```

For test coverage report:

```
pytest --cov=app --cov-report=html
```

This will generate an HTML coverage report in the `htmlcov/` directory.

## Test Coverage Report

The current test coverage is **79%** overall. Key coverage metrics:

| Module | Coverage |
|--------|----------|
| App Models | 100% |
| LLM Singleton | 100% |
| LLM Manager | 96% |
| Main App | 96% |
| Chatbot Services | 56% |
| Chatbot Router | 57% |
| Error Handler | 69% |
| Logger | 87% |
| Game Services | 87-91% |

### Coverage Analysis

- **Well Tested Areas**:
  - Data models (100% coverage)
  - LLM singleton pattern (96-100%)
  - Application setup (96%)
  - Utility services (87-91%)

- **Areas Needing Improvement**:
  - Chatbot services (56%): Core functions like `call_model` and `handle_chatbot_request` need more tests
  - Chatbot router (57%): The streaming response mechanism is not fully tested
  - Error handling (69%): Some error cases are not covered

### Highest Priority Test Improvements:

1. Add tests for the `chatbot_services.py` module, particularly:
   - The LangGraph workflow execution
   - Response streaming functionality
   - Error handling scenarios

2. Improve router testing for streaming responses

3. Enhance test mocking of LLM response formats

## Project Structure

```
gonext-ml/
├── app/
│   ├── models/         # Pydantic models and data structures
│   ├── routers/        # API endpoints and route handlers
│   ├── services/       # Business logic and services
│   ├── llm/            # LLM integration and abstraction
│   ├── utils/          # Utilities, logging, and error handling
│   ├── config.py       # Configuration settings
│   ├── dependencies.py # Dependency injection
│   └── main.py         # Application entry point
├── tests/              # Test suite
├── .env                # Environment variables (not in version control)
├── .env.sample         # Sample environment file
├── requirements.txt    # Dependencies
└── README.md           # This file
```

## Key Components

### Chatbot Service

The chatbot service uses LangGraph for conversation management with these components:

1. **System Prompt**: Configurable template with language support that instructs the LLM to act as a League of Legends assistant
2. **State Management**: Thread-based conversation state with message history
3. **LLM Abstraction**: Singleton pattern for managing multiple LLM providers (OpenAI and Google Gemini)
4. **Response Streaming**: FastAPI streaming responses for real-time chat interaction

### LLM Integration

The system supports multiple LLM providers through a singleton pattern:

- **OpenAI**: GPT-4o-mini model
- **Google**: Gemini 2.0 Flash model
- Extendable to support additional models

### Error Handling

Comprehensive error handling with custom error types:
- `ServiceUnavailableError`: For LLM service issues
- `InvalidInputError`: For input validation failures

## Screenshots

![Chatbot Interface](https://github.com/user-attachments/assets/dacc5906-e871-4150-a780-723c81e2d362)

![Game Analysis](https://github.com/user-attachments/assets/205a5b4c-8dd4-439d-821f-9ddc5dd57c35)

## Contributing

1. Fork the repository
2. Create a feature branch: `git checkout -b feature/your-feature-name`
3. Commit your changes: `git commit -m 'Add some feature'`
4. Push to the branch: `git push origin feature/your-feature-name`
5. Submit a pull request

## License

This project is licensed under the MIT License - see the LICENSE file for details.





