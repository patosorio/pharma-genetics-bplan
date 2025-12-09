from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from sqlalchemy import and_
from typing import Optional
from datetime import datetime, date

from src.core.db import get_db
from src.services.google_sheets import sync_data
from src.core.shared.exceptions import InternalServerError, ValidationError
from src.models.expenses import Expense
from src.models.income import Income
from src.api.v1.schemas.expenses import ExpenseListResponse, ExpenseResponse
from src.api.v1.schemas.income import IncomeListResponse, IncomeResponse


def parse_date_dd_mm_yyyy(date_str: Optional[str]) -> Optional[date]:
    """Parse date string in DD/MM/YYYY format to date object."""
    if date_str is None:
        return None
    
    try:
        # Try DD/MM/YYYY format (European)
        return datetime.strptime(date_str, "%d/%m/%Y").date()
    except ValueError:
        raise ValidationError(
            detail=f"Invalid date format: '{date_str}'. Expected DD/MM/YYYY (e.g., 25/12/2025)",
            context={"provided_value": date_str, "expected_format": "DD/MM/YYYY"}
        )

router = APIRouter(prefix='/api/v1')

# Sync endpoint
@router.post('/sync', tags=['Sync'])
async def trigger_sync(db: Session = Depends(get_db)):
    """Trigger synchronization from Google Sheets to database."""
    try:
        result = sync_data(db)
        return result
    except Exception as e:
        raise InternalServerError(detail=str(e))


# Income endpoints
@router.get('/income', response_model=IncomeListResponse, tags=['Income'])
async def list_income(
    db: Session = Depends(get_db),
    start_date: Optional[str] = Query(None, description="Filter income from this date (inclusive). Format: DD/MM/YYYY (e.g., 01/12/2025)"),
    end_date: Optional[str] = Query(None, description="Filter income until this date (inclusive). Format: DD/MM/YYYY (e.g., 31/12/2025)"),
    location: Optional[str] = Query(None, description="Filter by location"),
):
    """
    List all income records with optional filters.
    
    Date Format: DD/MM/YYYY (European format, e.g., 25/12/2025)
    
    Filters:
    - start_date: Include records with doc_date >= start_date (DD/MM/YYYY)
    - end_date: Include records with doc_date <= end_date (DD/MM/YYYY)
    - location: Filter by exact location match
    
    Examples:
    - /api/v1/income?start_date=01/12/2025&end_date=31/12/2025
    - /api/v1/income?location=Bkk
    """
    try:
        # Parse dates from DD/MM/YYYY format
        start_date_obj = parse_date_dd_mm_yyyy(start_date)
        end_date_obj = parse_date_dd_mm_yyyy(end_date)
        
        # Build query with filters
        query = db.query(Income)
        
        filters = []
        if start_date_obj:
            filters.append(Income.doc_date >= start_date_obj)
        if end_date_obj:
            filters.append(Income.doc_date <= end_date_obj)
        if location:
            filters.append(Income.location == location)
        
        if filters:
            query = query.filter(and_(*filters))
        
        # Order by doc_date descending (most recent first)
        query = query.order_by(Income.doc_date.desc())
        
        # Execute query
        income_records = query.all()
        
        # Prepare response
        return IncomeListResponse(
            total=len(income_records),
            income=[IncomeResponse.model_validate(record) for record in income_records],
            filters_applied={
                "start_date": start_date,
                "end_date": end_date,
                "location": location,
            }
        )
    except ValidationError:
        raise
    except Exception as e:
        raise InternalServerError(detail=f"Failed to retrieve income records: {str(e)}")


# Expense endpoints
@router.get('/expenses', response_model=ExpenseListResponse, tags=['Expenses'])
async def list_expenses(
    db: Session = Depends(get_db),
    start_date: Optional[str] = Query(None, description="Filter expenses from this date (inclusive). Format: DD/MM/YYYY (e.g., 01/12/2025)"),
    end_date: Optional[str] = Query(None, description="Filter expenses until this date (inclusive). Format: DD/MM/YYYY (e.g., 31/12/2025)"),
    location: Optional[str] = Query(None, description="Filter by location"),
):
    """
    List all expense records with optional filters.
    
    Date Format: DD/MM/YYYY (European format, e.g., 25/12/2025)
    
    Filters:
    - start_date: Include records with doc_date >= start_date (DD/MM/YYYY)
    - end_date: Include records with doc_date <= end_date (DD/MM/YYYY)
    - location: Filter by exact location match
    
    Examples:
    - /api/v1/expenses?start_date=01/12/2025&end_date=31/12/2025
    - /api/v1/expenses?location=Pattaya
    """
    try:
        # Parse dates from DD/MM/YYYY format
        start_date_obj = parse_date_dd_mm_yyyy(start_date)
        end_date_obj = parse_date_dd_mm_yyyy(end_date)
        
        # Build query with filters
        query = db.query(Expense)
        
        filters = []
        if start_date_obj:
            filters.append(Expense.doc_date >= start_date_obj)
        if end_date_obj:
            filters.append(Expense.doc_date <= end_date_obj)
        if location:
            filters.append(Expense.location == location)
        
        if filters:
            query = query.filter(and_(*filters))
        
        # Order by doc_date descending (most recent first)
        query = query.order_by(Expense.doc_date.desc())
        
        # Execute query
        expense_records = query.all()
        
        # Prepare response
        return ExpenseListResponse(
            total=len(expense_records),
            expenses=[ExpenseResponse.model_validate(record) for record in expense_records],
            filters_applied={
                "start_date": start_date,
                "end_date": end_date,
                "location": location,
            }
        )
    except ValidationError:
        raise
    except Exception as e:
        raise InternalServerError(detail=f"Failed to retrieve expense records: {str(e)}")