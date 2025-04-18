# GoNext - League of Legends Assistant API

This is the ML server for GONEXT - a GenAI-powered assistant tailored for League of Legends players.

**GONEXT** delivers real-time and personalized strategies, matchups, synergies, and builds. By harnessing the Riot API, GoNext retrieves live game data—covering both allied and enemy players—and employs large language models to offer context-specific guidance for every match.

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

## Screenshots

![Chatbot Interface](https://github.com/user-attachments/assets/dacc5906-e871-4150-a780-723c81e2d362)

![Game Analysis](https://github.com/user-attachments/assets/205a5b4c-8dd4-439d-821f-9ddc5dd57c35)

![Champion Recommendations](https://github.com/user-attachments/assets/961bc52b-f289-40e1-8e7d-0d1c48178033)

![Performance Analysis](https://github.com/user-attachments/assets/0c7c618f-7c1f-408b-80ad-6a77fb56e626)

## Contributing

1. Fork the repository
2. Create a feature branch: `git checkout -b feature/your-feature-name`
3. Commit your changes: `git commit -m 'Add some feature'`
4. Push to the branch: `git push origin feature/your-feature-name`
5. Submit a pull request

## License

This project is licensed under the MIT License - see the LICENSE file for details.





