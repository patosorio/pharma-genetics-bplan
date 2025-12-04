import enum

from sqlalchemy.sql import func
from sqlalchemy import (
    Column,
    Integer,
    String,
    Date,
    Numeric,
    Enum,
    DateTime,
    ForeignKey,
    Index,
)

from ..core.db import Base


class IncomeStatus(str, enum.Enum):
    """Status of an income document."""
    PAID = "Paid"
    PENDING = "Pending"
    OVERDUE = "Overdue"
    CANCELLED = "Cancelled"


class Income(Base):
    __tablename__ = "income"

    id = Column(Integer, primary_key=True, index=True)

    # Core document data
    doc_no = Column(String, unique=True, nullable=False, index=True)
    doc_date = Column(Date, nullable=False, index=True)
    customer = Column(String, nullable=False)
    currency = Column(String(3), nullable=False, default="THB")

    # Amounts (stored as Decimal for precision)
    amount = Column(Numeric(12, 2), nullable=False)        # Net amount
    vat = Column(Numeric(12, 2), default=0.0)              # VAT amount
    grand_total = Column(Numeric(12, 2), nullable=False)    # amount + vat

    # Status & payment
    status = Column(Enum(IncomeStatus), default=IncomeStatus.PENDING, nullable=False)

    # Metadata for reporting & audit
    location = Column(String, nullable=False)  # Location A / Location B
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )
    created_by = Column(String, nullable=True)  # user / system
    notes = Column(String, nullable=True)

    # TODO: Add customer_id when customer table is created
    # customer_id = Column(Integer, ForeignKey("customers.id"), nullable=True)

    __table_args__ = (
        Index("ix_income_doc_date_location", "doc_date", "location"),
        Index("ix_income_status", "status"),
    )

    def __repr__(self) -> str:
        return f"<Income {self.doc_no} {self.grand_total} {self.status.value}>"
