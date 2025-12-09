"""Report endpoints for P&L and other financial reports."""

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from typing import Optional
from datetime import datetime

from src.core.db import get_db
from src.core.shared.exceptions import ValidationError, InternalServerError
from src.services.reports.pnl import ProfitAndLossService
from src.services.reports.cashflow import CashflowService
from src.api.v1.schemas.reports import PnLReportResponse, CashflowReportResponse

router = APIRouter(prefix='/api/v1/reports', tags=['Reports'])


def parse_date_dd_mm_yyyy(date_str: Optional[str]) -> Optional[datetime]:
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


@router.get('/pnl', response_model=PnLReportResponse)
async def get_profit_and_loss_report(
    db: Session = Depends(get_db),
    start_date: str = Query(
        ...,
        description="Start date for P&L report. Format: DD/MM/YYYY (e.g., 01/01/2025)"
    ),
    end_date: str = Query(
        ...,
        description="End date for P&L report. Format: DD/MM/YYYY (e.g., 31/12/2025)"
    ),
    format: str = Query(
        'yearly',
        description="Report format: 'yearly' (single Total column) or 'monthly' (column per month)",
        regex="^(yearly|monthly)$"
    ),
    location: Optional[str] = Query(
        None,
        description="Filter by location. Use 'All' or leave empty for all locations"
    ),
):
    """
    Generate Profit & Loss (P&L) report.
    
    The P&L report includes:
    - **Revenue**: Broken down by customer
    - **COGS**: Cost of Goods Sold, grouped by category/subcategory
    - **Gross Profit**: Revenue - COGS
    - **Operating Expenses**: OPEX grouped by category/subcategory
    - **EBIT**: Earnings Before Interest and Taxes
    - **Income Tax**: 15% of EBIT (0 if EBIT is negative)
    - **Net Earnings**: EBIT - Income Tax
    
    **Date Format**: DD/MM/YYYY (European format, e.g., 25/12/2025)
    
    **Date Range Limit**: Maximum 12 months
    
    **Format Options**:
    - `yearly`: Single "Total" column summing the entire period
    - `monthly`: One column per month (e.g., sep-24, oct-24, nov-24)
    
    **Notes**:
    - All amounts are base amounts (without VAT)
    - CAPEX expenses are NOT included in P&L
    - Only COGS and OPEX are included
    
    **Examples**:
    ```
    # Yearly report for all locations
    GET /api/v1/reports/pnl?start_date=01/01/2025&end_date=31/12/2025&format=yearly
    
    # Monthly report for specific location
    GET /api/v1/reports/pnl?start_date=01/09/2024&end_date=31/08/2025&format=monthly&location=Bkk
    ```
    """
    try:
        # Parse dates
        start_date_obj = parse_date_dd_mm_yyyy(start_date)
        end_date_obj = parse_date_dd_mm_yyyy(end_date)
        
        if not start_date_obj or not end_date_obj:
            raise ValidationError(
                detail="Both start_date and end_date are required",
                context={"start_date": start_date, "end_date": end_date}
            )
        
        # Handle location
        location_value = location if location else 'All'
        
        # Generate report using service
        pnl_service = ProfitAndLossService(db)
        report = pnl_service.generate_pnl_report(
            start_date=start_date_obj,
            end_date=end_date_obj,
            format_type=format,
            location=location_value
        )
        
        return PnLReportResponse(**report)
        
    except ValidationError:
        raise
    except Exception as e:
        raise InternalServerError(
            detail=f"Failed to generate P&L report: {str(e)}",
            context={"error_type": type(e).__name__}
        )


@router.get('/cashflow', response_model=CashflowReportResponse)
async def get_cashflow_report(
    db: Session = Depends(get_db),
    start_date: str = Query(
        ...,
        description="Start date for cashflow report. Format: DD/MM/YYYY (e.g., 01/01/2025)"
    ),
    end_date: str = Query(
        ...,
        description="End date for cashflow report. Format: DD/MM/YYYY (e.g., 31/12/2025)"
    ),
    format: str = Query(
        'yearly',
        description="Report format: 'yearly' (single Total column) or 'monthly' (column per month)",
        regex="^(yearly|monthly)$"
    ),
    location: Optional[str] = Query(
        None,
        description="Filter by location. Use 'All' or leave empty for all locations"
    ),
    opening_balance: float = Query(
        0.0,
        description="Opening cash balance for the period (default: 0.0)"
    ),
):
    """
    Generate Cashflow report.
    
    The Cashflow report includes:
    - **Cash Inflows**: Sales income (with VAT), Fundings, Other income
    - **Cash Outflows**: COGS, OPEX, and CAPEX (all grouped by category/subcategory)
    - **Net Cashflow**: Total Inflows - Total Outflows
    - **Opening Balance**: Starting cash position
    - **Closing Balance**: Opening Balance + Net Cashflow
    
    **Date Format**: DD/MM/YYYY (European format, e.g., 25/12/2025)
    
    **Date Range Limit**: Maximum 12 months
    
    **Format Options**:
    - `yearly`: Single "Total" column summing the entire period
    - `monthly`: One column per month with cumulative balances
    
    **Notes**:
    - All amounts include VAT (grand_total column)
    - CAPEX is included in cashflow (unlike P&L)
    - For monthly format, opening/closing balances are calculated cumulatively
    
    **Examples**:
    ```
    # Yearly cashflow for all locations
    GET /api/v1/reports/cashflow?start_date=01/01/2025&end_date=31/12/2025&format=yearly
    
    # Monthly cashflow with opening balance
    GET /api/v1/reports/cashflow?start_date=01/11/2025&end_date=31/12/2025&format=monthly&opening_balance=50000
    
    # Cashflow for specific location
    GET /api/v1/reports/cashflow?start_date=01/09/2024&end_date=31/08/2025&format=monthly&location=Bkk
    ```
    """
    try:
        # Parse dates
        start_date_obj = parse_date_dd_mm_yyyy(start_date)
        end_date_obj = parse_date_dd_mm_yyyy(end_date)
        
        if not start_date_obj or not end_date_obj:
            raise ValidationError(
                detail="Both start_date and end_date are required",
                context={"start_date": start_date, "end_date": end_date}
            )
        
        # Handle location
        location_value = location if location else 'All'
        
        # Generate report using service
        cashflow_service = CashflowService(db)
        report = cashflow_service.generate_cashflow_report(
            start_date=start_date_obj,
            end_date=end_date_obj,
            format_type=format,
            location=location_value,
            opening_balance=opening_balance
        )
        
        return CashflowReportResponse(**report)
        
    except ValidationError:
        raise
    except Exception as e:
        raise InternalServerError(
            detail=f"Failed to generate cashflow report: {str(e)}",
            context={"error_type": type(e).__name__}
        )

