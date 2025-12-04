# Hi Tai Business Plan Dashboard API

Temporary API for reporting and visualizing business plan data from Google Spreadsheets.

## Tech Stack

- **FastAPI** - Modern, fast web framework for building APIs
- **SQLAlchemy** - SQL toolkit and ORM
- **Alembic** - Database migration tool
- **Pydantic** - Data validation using Python type annotations
- **Uvicorn** - ASGI server

## Project Structure

```
hitai-bplan/
├── src/
│   ├── main.py                    # FastAPI application entry point
│   └── core/
│       ├── config.py              # Application settings and configuration
│       ├── db.py                  # Database connection and session management
│       └── shared/
│           ├── exceptions.py      # Custom exception classes
│           └── exceptions_handler.py  # Global exception handlers
├── alembic/                       # Database migrations
│   └── env.py                     # Alembic environment configuration
├── alembic.ini                    # Alembic configuration file
├── requirements.txt               # Python dependencies
└── pyproject.toml                 # Project configuration and tool settings
```

## Setup

### Prerequisites

- Python 3.9+
- Virtual environment (recommended)

### Installation

1. Clone the repository:
```bash
git clone <repository-url>
cd hitai-bplan
```

2. Create and activate a virtual environment:
```bash
python -m venv env
source env/bin/activate  # On Windows: env\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Create a `.env` file in the root directory:
```env
ENV=development
SECRET_KEY=your-secret-key-here
```

### Database Setup

The application uses SQLite by default. The database file (`hitai_bi.db`) will be created automatically on first run.

To run database migrations:
```bash
alembic upgrade head
```

## Running the Application

Run the FastAPI server:
```bash
python -m src.main
```

Or using uvicorn directly:
```bash
uvicorn src.main:app --host 0.0.0.0 --port 8000 --reload
```

The API will be available at:
- API: http://localhost:8000
- Interactive docs: http://localhost:8000/docs (development only)
- Health check: http://localhost:8000/health

## API Endpoints

### Root
- `GET /` - Welcome message and API information

### Health
- `GET /health` - Health check endpoint for monitoring

### Development
- `GET /test-exceptions?exception_type={type}` - Test exception handling (development only)
  - Available types: `validation`, `notfound`, `badrequest`, `unauthorized`, `internal`

## Features

- **Structured Exception Handling**: Custom exception classes with consistent error responses
- **Database Integration**: SQLAlchemy ORM with Alembic migrations
- **Environment-based Configuration**: Settings managed via Pydantic and `.env` files
- **Logging**: Configured logging for application events and errors
- **Health Monitoring**: Health check endpoint for service monitoring

## Configuration

Application settings are managed through environment variables in `.env`:

- `ENV` - Environment (development/production)
- `SECRET_KEY` - Secret key for security
- `API_HOST` - API host (default: 0.0.0.0)
- `API_PORT` - API port (default: 8000)
- `DEBUG` - Debug mode (default: True)

## Development

The project includes:
- **Ruff** - Fast Python linter
- **Black** - Code formatter (configured in pyproject.toml)
- **MyPy** - Static type checking

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.
