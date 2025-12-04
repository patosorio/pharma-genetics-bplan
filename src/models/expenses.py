from sqlalchemy import (
    Column,
    Boolean,
    Integer,
    String,
    Date,
    Numeric,
    Enum,
    DateTime,
    ForeignKey,
    Index,
    func,
)
from sqlalchemy.orm import relationship
from ..core.db import Base

import enum


class ExpenseStatus(str, enum.Enum):
    PENDING = "Pending"
    PAID = "Paid"
    OVERDUE = "Overdue"
    CANCELLED = "Cancelled"


class ExpenseType(str, enum.Enum):
    CAPEX = "CAPEX"
    OPEX = "OPEX"
    COGS = "COGS"


class ExpenseCategory(Base):
    __tablename__ = "expense_categories"

    id = Column(Integer, primary_key=True)
    name = Column(String, nullable=False, unique=True)
    parent_id = Column(Integer, ForeignKey("expense_categories.id"), nullable=True)

    # Relationship to children and parent
    parent = relationship("ExpenseCategory", remote_side=[id], back_populates="children")
    children = relationship("ExpenseCategory", back_populates="parent")

    def __repr__(self):
        return f"<Category {self.name}>"


# Main expenses table
class Expense(Base):
    __tablename__ = "expenses"

    id = Column(Integer, primary_key=True, index=True)

    # Document info
    doc_no = Column(String, unique=True, nullable=False, index=True)
    doc_date = Column(Date, nullable=False, index=True)
    overdue_date = Column(Date, nullable=True)

    # Counterparty
    supplier = Column(String, nullable=False)

    # Money
    currency = Column(String(3), nullable=False, default="THB")
    amount = Column(Numeric(12, 2), nullable=False)
    vat = Column(Numeric(12, 2), default=0.0)
    grand_total = Column(Numeric(12, 2), nullable=False)

    # Classification
    status = Column(Enum(ExpenseStatus), default=ExpenseStatus.PENDING, nullable=False)
    type = Column(Enum(ExpenseType), nullable=False)       # CAPEX / OPEX / COGS
    location = Column(String, nullable=False)

    # Hierarchical category
    category_id = Column(Integer, ForeignKey("expense_categories.id"), nullable=False)
    category = relationship("ExpenseCategory")
    subcategory_free = Column(String, nullable=True)

    # Recurrency & forecasting
    is_recurring = Column(Boolean, default=False, nullable=False, index=True)
    recurrence_period = Column(String, nullable=True)
    forecasted_until = Column(Date, nullable=True)

    # Metadata & audit
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    created_by = Column(String, nullable=True)
    notes = Column(String, nullable=True)

    __table_args__ = (
        Index("ix_expenses_doc_date", "doc_date"),
        Index("ix_expenses_type", "type"),
        Index("ix_expenses_location", "location"),
        Index("ix_expenses_category", "category_id"),
    )

    def __repr__(self):
        return f"<Expense {self.doc_no} {self.grand_total} {self.type.value}>"
