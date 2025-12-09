from pydantic import BaseModel, Field, ConfigDict
from typing import Optional
from datetime import date, datetime
from decimal import Decimal


class IncomeResponse(BaseModel):
    """Response schema for income data."""
    
    model_config = ConfigDict(from_attributes=True)
    
    id: int
    row_id: Optional[str] = None
    doc_no: str
    doc_date: date
    customer: str
    currency: str
    amount: Decimal
    vat: Decimal
    grand_total: Decimal
    status: str
    location: str
    created_at: datetime
    updated_at: datetime
    created_by: Optional[str] = None
    notes: Optional[str] = None


class IncomeListResponse(BaseModel):
    """Response schema for list of income records."""
    
    total: int = Field(..., description="Total number of income records matching the filters")
    income: list[IncomeResponse] = Field(..., description="List of income records")
    filters_applied: dict = Field(..., description="Filters that were applied to the query")

