# SWEG Project

A Python project for Software Engineering coursework.

## Setup

### 1. Create a virtual environment

```bash
# Windows
python -m venv venv
venv\Scripts\activate

# Linux/Mac
python -m venv venv
source venv/bin/activate
```

### 2. Install dependencies

```bash
# Install project dependencies
pip install -r requirements.txt

# Install development dependencies
pip install -r requirements-dev.txt

# Or install everything including dev dependencies
pip install -e ".[dev]"
```

### 3. Install the project in development mode

```bash
pip install -e .
```

## Development

### Running the code

```bash
python -m sweg_project.main
```

### Running tests

```bash
# Run all tests
pytest

# Run tests with coverage
pytest --cov=src --cov-report=html

# Run specific test file
pytest tests/test_main.py
```

### Code formatting and linting

```bash
# Format code with black
black src tests

# Check code style with flake8
flake8 src tests

# Type checking with mypy
mypy src
```

### Pre-commit hooks (optional)

```bash
# Install pre-commit hooks
pre-commit install

# Run pre-commit on all files
pre-commit run --all-files
```

## Project Structure

```
SWEG_project/
├── src/
│   └── sweg_project/
│       ├── __init__.py
│       └── main.py
├── tests/
│   ├── __init__.py
│   └── test_main.py
├── dist/
├── .git/
├── pyproject.toml
├── requirements.txt
├── requirements-dev.txt
└── README.md
```

## Contributing

1. Create a feature branch
2. Make your changes
3. Add tests for new functionality
4. Run tests and ensure they pass
5. Format code with black
6. Commit and push your changes
7. Create a pull request

## License

This project is licensed under the MIT License.