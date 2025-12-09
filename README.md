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
│   │       ├── router.py          # API routes (income, expenses, sync)
│   │       └── schemas/           # Pydantic schemas for request/response
│   │           ├── expenses.py    # Expense response schemas
│   │           └── income.py      # Income response schemas
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
- `POST /api/v1/sync` - Sync data from Google Sheets to local database
  - Syncs income, expenses, and pending investments
  - Returns summary with counts of inserted/updated/skipped records
  - Calculates total income, expenses, and net position

### Income
- `GET /api/v1/income` - List all income records with optional filters
  - **Query Parameters:**
    - `start_date` (optional, format: DD/MM/YYYY) - Filter records from this date (inclusive)
    - `end_date` (optional, format: DD/MM/YYYY) - Filter records until this date (inclusive)
    - `location` (optional, string) - Filter by exact location match
  - **Response:** JSON with total count, list of income records, and applied filters
  - **Date Format:** European format DD/MM/YYYY (e.g., 25/12/2025)
  - **Example:**
    ```bash
    # Get all income
    curl http://localhost:8000/api/v1/income
    
    # Filter by date range (DD/MM/YYYY format)
    curl "http://localhost:8000/api/v1/income?start_date=01/12/2025&end_date=31/12/2025"
    
    # Filter by location
    curl "http://localhost:8000/api/v1/income?location=Bkk"
    
    # Combine filters
    curl "http://localhost:8000/api/v1/income?start_date=01/12/2025&location=Bkk"
    ```

### Expenses
- `GET /api/v1/expenses` - List all expense records with optional filters
  - **Query Parameters:**
    - `start_date` (optional, format: DD/MM/YYYY) - Filter records from this date (inclusive)
    - `end_date` (optional, format: DD/MM/YYYY) - Filter records until this date (inclusive)
    - `location` (optional, string) - Filter by exact location match
  - **Response:** JSON with total count, list of expense records, and applied filters
  - **Date Format:** European format DD/MM/YYYY (e.g., 25/12/2025)
  - **Example:**
    ```bash
    # Get all expenses
    curl http://localhost:8000/api/v1/expenses
    
    # Filter by date range (DD/MM/YYYY format)
    curl "http://localhost:8000/api/v1/expenses?start_date=01/12/2025&end_date=31/12/2025"
    
    # Filter by location
    curl "http://localhost:8000/api/v1/expenses?location=Pattaya"
    
    # Combine filters
    curl "http://localhost:8000/api/v1/expenses?start_date=01/12/2025&location=Pattaya"
    ```

### Reports

#### Profit & Loss (P&L) Report
- `GET /api/v1/reports/pnl` - Generate P&L report with breakdown by customer and categories
  - **Query Parameters:**
    - `start_date` (required, format: DD/MM/YYYY) - Start date for report
    - `end_date` (required, format: DD/MM/YYYY) - End date for report (max 12 months from start_date)
    - `format` (required) - Report format: `yearly` or `monthly`
    - `location` (optional, string) - Filter by location (use 'All' or leave empty for all locations)
  - **Date Format:** European format DD/MM/YYYY (e.g., 25/12/2025)
  - **Date Range Limit:** Maximum 12 months between start_date and end_date
  - **P&L Structure:**
    - **Revenue**: Broken down by customer with totals
    - **COGS**: Cost of Goods Sold, grouped by category → subcategory
    - **Gross Profit**: Revenue - COGS
    - **Operating Expenses (OPEX)**: Grouped by category → subcategory
    - **EBIT**: Earnings Before Interest and Taxes (Gross Profit - OPEX)
    - **Income Tax**: 15% of EBIT (0 if EBIT is negative)
    - **Net Earnings**: EBIT - Income Tax
  - **Format Options:**
    - `yearly`: Single "Total" column summing the entire period
    - `monthly`: One column per month (e.g., nov-25, dec-25)
  - **Notes:**
    - All amounts use base values (without VAT)
    - CAPEX expenses are NOT included in P&L
    - Only COGS and OPEX expenses are included
  - **Example:**
    ```bash
    # Yearly P&L for all locations
    curl "http://localhost:8000/api/v1/reports/pnl?start_date=01/01/2025&end_date=31/12/2025&format=yearly"
    
    # Monthly P&L for specific location
    curl "http://localhost:8000/api/v1/reports/pnl?start_date=01/11/2025&end_date=31/12/2025&format=monthly&location=Bkk"
    
    # Quarterly P&L (Sep-Nov 2024)
    curl "http://localhost:8000/api/v1/reports/pnl?start_date=01/09/2024&end_date=30/11/2024&format=monthly"
    ```

#### Cashflow Report
- `GET /api/v1/reports/cashflow` - Generate cashflow report with inflows and outflows
  - **Query Parameters:**
    - `start_date` (required, format: DD/MM/YYYY) - Start date for report
    - `end_date` (required, format: DD/MM/YYYY) - End date for report (max 12 months from start_date)
    - `format` (required) - Report format: `yearly` or `monthly`
    - `location` (optional, string) - Filter by location (use 'All' or leave empty for all locations)
    - `opening_balance` (optional, float) - Opening cash balance (default: 0.0)
  - **Date Format:** European format DD/MM/YYYY (e.g., 25/12/2025)
  - **Date Range Limit:** Maximum 12 months between start_date and end_date
  - **Cashflow Structure:**
    - **Cash Inflows**: 
      - Sales Income (with VAT)
      - Fundings (placeholder for future)
      - Other Income (placeholder for future)
      - Total Inflows
    - **Cash Outflows**: 
      - COGS: Cost of Goods Sold grouped by category → subcategory
      - OPEX: Operating Expenses grouped by category → subcategory
      - CAPEX: Capital Expenses grouped by category → subcategory
      - Total Outflows
    - **Net Cashflow**: Total Inflows - Total Outflows
    - **Opening Balance**: Starting cash position
    - **Closing Balance**: Opening Balance + Net Cashflow
  - **Format Options:**
    - `yearly`: Single "Total" column summing the entire period
    - `monthly`: One column per month with cumulative balances (each month's closing becomes next month's opening)
  - **Notes:**
    - All amounts use grand_total (including VAT) - different from P&L
    - CAPEX is included in cashflow (unlike P&L which only shows COGS and OPEX)
    - For monthly format, balances are calculated cumulatively across periods
  - **Example:**
    ```bash
    # Yearly cashflow for all locations
    curl "http://localhost:8000/api/v1/reports/cashflow?start_date=01/01/2025&end_date=31/12/2025&format=yearly"
    
    # Monthly cashflow with opening balance
    curl "http://localhost:8000/api/v1/reports/cashflow?start_date=01/11/2025&end_date=31/12/2025&format=monthly&opening_balance=50000"
    
    # Cashflow for specific location
    curl "http://localhost:8000/api/v1/reports/cashflow?start_date=01/09/2024&end_date=31/08/2025&format=monthly&location=Bkk"
    ```

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
