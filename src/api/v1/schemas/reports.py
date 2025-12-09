"""Response schemas for report endpoints."""

from pydantic import BaseModel, Field
from typing import Dict, List, Any


class CashflowReportResponse(BaseModel):
    """Response schema for Cashflow report."""
    
    report_info: Dict[str, Any] = Field(
        ...,
        description="Report metadata including date range, format, and periods"
    )
    cash_inflows: Dict[str, Any] = Field(
        ...,
        description="Cash inflows including sales income, fundings, and other income"
    )
    cash_outflows: Dict[str, Any] = Field(
        ...,
        description="Cash outflows including COGS, OPEX, and CAPEX"
    )
    net_cashflow: Dict[str, float] = Field(
        ...,
        description="Net cashflow per period (Inflows - Outflows)"
    )
    opening_balance: Dict[str, float] = Field(
        ...,
        description="Opening cash balance per period"
    )
    closing_balance: Dict[str, float] = Field(
        ...,
        description="Closing cash balance per period (Opening + Net Cashflow)"
    )
    
    model_config = {
        "json_schema_extra": {
            "example": {
                "report_info": {
                    "start_date": "2024-01-01",
                    "end_date": "2024-12-31",
                    "format": "yearly",
                    "location": "All",
                    "periods": ["Total"],
                    "generated_at": "2024-12-09T12:00:00"
                },
                "cash_inflows": {
                    "sales_income": {"Total": 150000.0},
                    "fundings": {"Total": 0.0},
                    "other_income": {"Total": 0.0},
                    "total_inflows": {"Total": 150000.0}
                },
                "cash_outflows": {
                    "cogs": {
                        "expenses_by_category": {},
                        "total": {"Total": 30000.0}
                    },
                    "opex": {
                        "expenses_by_category": {},
                        "total": {"Total": 50000.0}
                    },
                    "capex": {
                        "expenses_by_category": {},
                        "total": {"Total": 20000.0}
                    },
                    "total_outflows": {"Total": 100000.0}
                },
                "net_cashflow": {"Total": 50000.0},
                "opening_balance": {"Total": 10000.0},
                "closing_balance": {"Total": 60000.0}
            }
        }
    }


class PnLReportResponse(BaseModel):
    """Response schema for P&L report."""
    
    report_info: Dict[str, Any] = Field(
        ...,
        description="Report metadata including date range, format, and periods"
    )
    revenue: Dict[str, Any] = Field(
        ...,
        description="Revenue section with breakdown by customer"
    )
    cogs: Dict[str, Any] = Field(
        ...,
        description="Cost of Goods Sold section grouped by category/subcategory"
    )
    gross_profit: Dict[str, float] = Field(
        ...,
        description="Gross Profit per period (Revenue - COGS)"
    )
    operating_expenses: Dict[str, Any] = Field(
        ...,
        description="Operating Expenses (OPEX) grouped by category/subcategory"
    )
    ebit: Dict[str, float] = Field(
        ...,
        description="Earnings Before Interest and Taxes per period"
    )
    income_tax: Dict[str, float] = Field(
        ...,
        description="Income Tax (15% of EBIT if positive, 0 if negative)"
    )
    net_earnings: Dict[str, float] = Field(
        ...,
        description="Net Earnings per period (EBIT - Income Tax)"
    )
    
    model_config = {
        "json_schema_extra": {
            "example": {
                "report_info": {
                    "start_date": "2024-01-01",
                    "end_date": "2024-12-31",
                    "format": "yearly",
                    "location": "All",
                    "periods": ["Total"],
                    "generated_at": "2024-12-09T12:00:00"
                },
                "revenue": {
                    "revenue_by_customer": {
                        "Customer A": {"Total": 100000.0},
                        "Customer B": {"Total": 50000.0}
                    },
                    "total_net_revenue": {"Total": 150000.0}
                },
                "cogs": {
                    "expenses_by_category": {
                        "Materials": {
                            "subcategories": {
                                "Raw Materials": {"Total": 30000.0}
                            }
                        }
                    },
                    "total": {"Total": 30000.0}
                },
                "gross_profit": {"Total": 120000.0},
                "operating_expenses": {
                    "expenses_by_category": {
                        "Salaries": {
                            "direct": {"Total": 50000.0}
                        }
                    },
                    "total": {"Total": 50000.0}
                },
                "ebit": {"Total": 70000.0},
                "income_tax": {"Total": 10500.0},
                "net_earnings": {"Total": 59500.0}
            }
        }
    }

