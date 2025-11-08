# SWEG Project

A Python project for Software Engineering coursework with SQLAlchemy ORM integration for post management.

## Features

- **User Management**: Create and manage users with unique usernames and emails
- **Post Management**: Create, retrieve, and manage posts with text, images, and user relationships
- **Database Integration**: SQLAlchemy ORM with SQLite database
- **European Timezone**: All timestamps use European timezone (Europe/Berlin)
- **Comprehensive Testing**: Unit tests for all major functionality

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
# Run the main application (demonstrates post management)
python -m sweg_project.main
```

This will:
- Create a sample user
- Create multiple posts with different content
- Display the latest post
- Show all posts with user information

### Running tests

```bash
# Run all tests
pytest

# Run tests with verbose output
pytest -v

# Run specific test file
pytest tests/test_main.py -v

# Run a specific test class
pytest tests/test_main.py::TestDatabaseService -v

# Run a specific test method
pytest tests/test_main.py::TestDatabaseService::test_create_user -v
```

**Test Coverage:**
- **DatabaseService Tests**: User creation, post management, data retrieval
- **Models Tests**: European timezone functionality, string representations
- **Integration Tests**: Complete workflow from user creation to post retrieval

All tests use temporary databases and are isolated from each other.

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
│       ├── main.py          # Main application entry point
│       ├── models.py        # SQLAlchemy database models (User, Post)
│       └── database.py      # Database service layer
├── tests/
│   ├── __init__.py
│   └── test_main.py         # Comprehensive unit tests
├── posts.db                 # SQLite database (created automatically)
├── .git/
├── pyproject.toml
├── requirements.txt         # Core dependencies (SQLAlchemy)
├── requirements-dev.txt     # Development dependencies (pytest, etc.)
└── README.md
```

## Database Schema

**Users Table:**
- `id`: Primary key (auto-increment)
- `username`: Unique username (max 50 chars)
- `email`: Unique email (max 100 chars)
- `created_at`: Creation timestamp (European timezone)

**Posts Table:**
- `id`: Primary key (auto-increment)
- `title`: Post title (max 200 chars)
- `text`: Post content (text)
- `image`: Optional image URL/path (max 500 chars)
- `user_id`: Foreign key to Users table
- `created_at`: Creation timestamp (European timezone)

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