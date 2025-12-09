from pydantic import BaseModel, Field, ConfigDict
from typing import Optional
from datetime import date, datetime
from decimal import Decimal


class ExpenseResponse(BaseModel):
    """Response schema for expense data."""
    
    model_config = ConfigDict(from_attributes=True)
    
    id: int
    row_id: Optional[str] = None
    doc_no: str
    doc_date: date
    overdue_date: Optional[date] = None
    supplier: str
    currency: str
    amount: Decimal
    vat: Decimal
    grand_total: Decimal
    status: str
    type: str
    location: str
    category_id: int
    subcategory_free: Optional[str] = None
    is_recurring: bool
    recurrence_period: Optional[str] = None
    forecasted_until: Optional[date] = None
    created_at: datetime
    updated_at: datetime
    created_by: Optional[str] = None
    notes: Optional[str] = None


class ExpenseListResponse(BaseModel):
    """Response schema for list of expenses."""
    
    total: int = Field(..., description="Total number of expenses matching the filters")
    expenses: list[ExpenseResponse] = Field(..., description="List of expense records")
    filters_applied: dict = Field(..., description="Filters that were applied to the query")

