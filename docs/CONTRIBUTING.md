# Contributing to GONEXT

Thank you for your interest in contributing to GONEXT! This document provides guidelines and instructions for contributing to the project.

## Code of Conduct

By participating in this project, you agree to abide by our Code of Conduct. Please be respectful and considerate of others.

## How to Contribute

### 1. Reporting Issues

Before creating an issue, please:
- Search existing issues to avoid duplicates
- Check if the issue has been fixed in the latest version
- Provide detailed information about the problem

When creating an issue, include:
- A clear, descriptive title
- Steps to reproduce the issue
- Expected and actual behavior
- Environment details (Python version, OS, etc.)
- Any relevant error messages or logs

### 2. Feature Requests

For feature requests:
- Explain the feature and why it's valuable
- Provide use cases and examples
- Consider suggesting an implementation approach

### 3. Pull Requests

#### Before Submitting a PR

1. Fork the repository
2. Create a feature branch: `git checkout -b feature/your-feature-name`
3. Install dependencies: `pip install -r requirements.txt`
4. Run tests: `pytest`
5. Format code: `black .`

#### PR Guidelines

- Keep PRs focused and small
- Include tests for new features
- Update documentation as needed
- Follow the existing code style
- Update CHANGELOG.md
- Ensure all tests pass locally

### 4. Code Style

We follow PEP 8 guidelines and use:
- `black` for code formatting
- `flake8` for linting
- `mypy` for type checking

Run these tools before submitting a PR:
```bash
black .
flake8
mypy .
```

### 5. Testing

- Write tests for new features
- Ensure all tests pass locally
- Maintain or improve test coverage
- Include both unit and integration tests

### 6. Documentation

- Update relevant documentation
- Add docstrings to new functions/classes
- Update README if needed
- Keep comments clear and concise

## Development Setup

1. Fork and clone the repository
2. Create a virtual environment
3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   pip install -r requirements-dev.txt
   ```
4. Set up pre-commit hooks:
   ```bash
   pre-commit install
   ```

## Release Process

1. Update version in `pyproject.toml`
2. Update CHANGELOG.md
3. Create a release tag
4. Update documentation if needed

## Questions?

Feel free to:
- Open an issue
- Join our community chat
- Contact the maintainers

Thank you for contributing to GONEXT! 