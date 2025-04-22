# **GONEXT** - League of Legends Assistant API

[![Python Version](https://img.shields.io/badge/python-3.9%2B-blue)](https://www.python.org/downloads/)
[![License: CC BY-NC 4.0](https://img.shields.io/badge/License-CC%20BY--NC%204.0-lightgrey.svg)](https://creativecommons.org/licenses/by-nc/4.0/)
[![Code Coverage](https://img.shields.io/badge/coverage-79%25-green)](https://github.com/yourusername/gonext-ml)

This is the ML server for **GONEXT** - a GenAI-powered assistant tailored for League of Legends players.

**GONEXT** delivers real-time and personalized strategies, matchups, synergies, and builds. By harnessing the Riot API, **GONEXT** retrieves live game data—covering both allied and enemy players—and employs large language models to offer context-specific guidance for every match.

## Table of Contents

- [Features](#features)
- [Architecture](#architecture)
- [Getting Started](#getting-started)
- [Documentation](#documentation)
- [Testing](#testing)
- [Security](#security)
- [Contributing](#contributing)
- [Support](#support)
- [Acknowledgments](#acknowledgments)
- [License](#license)

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
- Riot Games API Key (for game data access)
- OpenAI API Key (for GPT models)
- Google Gemini API Key (for Gemini models)

### Installation

1. Clone the repository:
   ```bash
   git clone https://github.com/yourusername/gonext-ml.git
   cd gonext-ml
   ```

2. Create a virtual environment:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

4. Set up environment variables:
   ```bash
   cp .env.sample .env
   ```
   
   Edit `.env` to include your API keys:
   ```
   RIOT_API_KEY=your_riot_key_here
   OPENAI_API_KEY=your_openai_key_here
   GEMINI_API_KEY=your_gemini_key_here
   ```

### Running the Application

Start the development server:

```bash
uvicorn app.main:app --reload
```

The API will be available at http://localhost:8000

## Documentation

### API Documentation

Once the server is running, access the interactive API documentation at:

- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

### Architecture Documentation

For detailed architecture documentation, please refer to the [ARCHITECTURE.md](docs/ARCHITECTURE.md) file.

## Testing

Run tests using pytest:

```bash
pytest
```

For test coverage report:

```bash
pytest --cov=app --cov-report=html
```

This will generate an HTML coverage report in the `htmlcov/` directory.

### Test Coverage Report

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

## Security

### API Key Security

- Never commit API keys to version control
- Use environment variables for sensitive data
- Rotate API keys regularly
- Follow the principle of least privilege

### Rate Limiting

The application implements rate limiting to prevent abuse:
- Default: 100 requests per minute
- Configurable through environment variables

## Contributing

We welcome contributions from the community! Please follow these guidelines:

1. Fork the repository
2. Create a feature branch: `git checkout -b feature/your-feature-name`
3. Commit your changes: `git commit -m 'Add some feature'`
4. Push to the branch: `git push origin feature/your-feature-name`
5. Submit a pull request

### Pull Request Guidelines

- Ensure all tests pass
- Update documentation as needed
- Follow the existing code style
- Include tests for new features
- Update the CHANGELOG.md

### Code Style

We follow PEP 8 guidelines. Use `black` for code formatting:

```bash
black .
```

## Support

For support, please:

1. Check the [documentation](docs/)
2. Search existing [issues](https://github.com/yourusername/gonext-ml/issues)
3. Create a new issue if needed

## Acknowledgments

- [Riot Games](https://developer.riotgames.com/) for their API
- [OpenAI](https://openai.com/) for GPT models
- [Google](https://ai.google.dev/) for Gemini models
- [FastAPI](https://fastapi.tiangolo.com/) for the web framework

## License

This project is licensed under the Creative Commons Attribution-NonCommercial 4.0 International (CC BY-NC 4.0) license. This means you are free to:

- Share — copy and redistribute the material in any medium or format
- Adapt — remix, transform, and build upon the material

Under the following terms:

- Attribution — You must give appropriate credit, provide a link to the license, and indicate if changes were made. You may do so in any reasonable manner, but not in any way that suggests the licensor endorses you or your use.
- NonCommercial — You may not use the material for commercial purposes without explicit permission.

**Commercial Use**: If you wish to use this project for commercial purposes, please contact the author directly to discuss licensing terms.

See the [LICENSE](LICENSE) file for the full license text.





