# Hi Tai Business Plan Dashboard API

API for reporting and visualizing business plan data from Google Spreadsheets. The system syncs financial data (income, expenses, and pending investments) from Google Sheets into a local SQLite database for analysis and reporting.

## Tech Stack

- **FastAPI** - Modern, fast web framework for building APIs
- **SQLAlchemy** - SQL toolkit and ORM
- **Alembic** - Database migration tool
- **Pydantic** - Data validation using Python type annotations
- **Uvicorn** - ASGI server
- **Google Sheets API** - Integration for reading spreadsheet data
- **Pandas** - Data processing and manipulation

## Project Structure

```
hitai-bplan/
├── src/
│   ├── main.py                    # FastAPI application entry point
│   ├── api/
│   │   └── v1/
│   │       └── router.py          # API routes (sync endpoint)
│   ├── models/                    # SQLAlchemy database models
│   │   ├── expenses.py            # Expense and ExpenseCategory models
│   │   ├── income.py              # Income model
│   │   └── pending_investments.py # PendingInvestment model
│   ├── services/
│   │   └── google_sheets.py       # Google Sheets sync service
│   └── core/
│       ├── config.py              # Application settings and configuration
│       ├── db.py                  # Database connection and session management
│       ├── dependencies.py        # FastAPI dependencies
│       ├── googleapi/
│       │   └── sheets_client.py   # Google Sheets API client
│       └── shared/
│           ├── exceptions.py      # Custom exception classes
│           └── exceptions_handler.py  # Global exception handlers
├── alembic/                       # Database migrations
│   ├── env.py                     # Alembic environment configuration
│   └── versions/                  # Migration scripts
├── alembic.ini                    # Alembic configuration file
├── requirements.txt               # Python dependencies
├── pyproject.toml                 # Project configuration and tool settings
└── hitai_bi.db                    # SQLite database (auto-generated)
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
GOOGLE_SHEET_ID=your-google-sheet-id
GOOGLE_SERVICE_ACCOUNT_FILE=your-google-service-account-json-file-url
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

### Data Sync
- `POST /api/sync` - Sync data from Google Sheets to local database
  - Syncs income, expenses, and pending investments
  - Returns summary with counts of inserted/updated/skipped records
  - Calculates total income, expenses, and net position

### Development
- `GET /test-exceptions?exception_type={type}` - Test exception handling (development only)
  - Available types: `validation`, `notfound`, `badrequest`, `unauthorized`, `internal`

## Features

### Data Models

- **Income**: Tracks revenue with document numbers, dates, customers, amounts, VAT, and status
- **Expenses**: Manages expenses with hierarchical categories (parent/child), supplier information, expense types (CAPEX/OPEX/COGS), and recurring expense tracking
- **Pending Investments**: Tracks planned investments with reference codes, estimated costs, committed amounts, priorities, and status

### Core Functionality

- **Google Sheets Integration**: Automatic synchronization of financial data from Google Spreadsheets
- **Dynamic Category Management**: Automatically creates hierarchical expense categories from spreadsheet data
- **Recurring Expense Detection**: Identifies and flags recurring expenses based on category patterns
- **Row-based Sync**: Uses stable row IDs to track and update existing records without duplicates
- **Change Detection**: Only updates records when data has actually changed
- **Financial Summaries**: Calculates total income, expenses, and net position after sync

### Technical Features

- **Structured Exception Handling**: Custom exception classes with consistent error responses
- **Database Integration**: SQLAlchemy ORM with Alembic migrations
- **Environment-based Configuration**: Settings managed via Pydantic and `.env` files
- **Logging**: Configured logging for application events and errors
- **Health Monitoring**: Health check endpoint for service monitoring

## Configuration

Application settings are managed through environment variables in `.env`:

### Required Variables
- `ENV` - Environment (development/production)
- `SECRET_KEY` - Secret key for security
- `GOOGLE_SHEET_ID` - Google Spreadsheet ID to sync from
- `GOOGLE_SERVICE_ACCOUNT_FILE` - Path to Google Service Account JSON file

### Optional Variables
- `API_HOST` - API host (default: 0.0.0.0)
- `API_PORT` - API port (default: 8000)
- `DEBUG` - Debug mode (default: True)

### Google Sheets Setup

1. Create a Google Cloud Project and enable the Google Sheets API
2. Create a Service Account and download the JSON key file
3. Share your Google Spreadsheet with the service account email
4. Place the JSON file in the project and reference it in `.env`

## Database Schema

The application uses SQLite with the following main tables:

- **income**: Revenue records with document tracking
- **expenses**: Expense records with hierarchical categories
- **expense_categories**: Parent-child category hierarchy
- **pending_investments**: Planned investment tracking

All tables include:
- `row_id`: Stable identifier from Google Sheets for sync tracking
- `created_at` / `updated_at`: Automatic timestamp tracking
- Indexes on frequently queried fields (dates, status, location, etc.)

### Running Migrations

To apply database migrations:
```bash
alembic upgrade head
```

To create a new migration:
```bash
alembic revision --autogenerate -m "description of changes"
```

## Development

The project includes:
- **Ruff** - Fast Python linter
- **Black** - Code formatter (configured in pyproject.toml)
- **MyPy** - Static type checking

### Code Quality

Linting and formatting are configured in `pyproject.toml`. The project uses:
- Ruff for linting (E, W, F, I, C, B rules)
- Black for code formatting (88 character line length)
- MyPy for type checking (strict mode enabled)

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.
