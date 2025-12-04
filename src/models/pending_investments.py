from sqlalchemy import (
    Column,
    Integer,
    String,
    Date,
    Numeric,
    DateTime,
    Index,
)
from sqlalchemy.sql import func
from ..core.db import Base


class PendingInvestment(Base):
    __tablename__ = "pending_investments"

    id = Column(Integer, primary_key=True, index=True)

    # Unique reference (e.g. CAPEX-2025-001)
    ref_code = Column(String, unique=True, nullable=False, index=True)

    # Description of the investment
    description = Column(String, nullable=False)
    detailed_notes = Column(String, nullable=True)

    # Financials
    currency = Column(String(3), nullable=False, default="THB")
    estimated_cost = Column(Numeric(14, 2), nullable=False)
    committed_amount = Column(Numeric(14, 2), default=0.0)
    funding_source = Column(String, nullable=True)

    # Timeline
    target_start_date = Column(Date, nullable=True)
    expected_completion_date = Column(Date, nullable=True)

    # Priority & status
    priority = Column(
        String,
        nullable=False,
        default="Medium",
        comment="Critical / High / Medium / Low"
    )
    status = Column(
        String,
        nullable=False,
        default="Planned",
        comment="Planned / Approved / In Progress / Completed / Cancelled"
    )

    location = Column(String, nullable=False)

    # Metadata & audit
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )
    created_by = Column(String, nullable=True)

    __table_args__ = (
        Index("ix_pending_investments_location", "location"),
        Index("ix_pending_investments_status", "status"),
        Index("ix_pending_investments_priority", "priority"),
    )

    @property
    def remaining_to_fund(self) -> float:
        return float(self.estimated_cost - self.committed_amount)

    def __repr__(self) -> str:
        return f"<PendingInvestment {self.ref_code} {self.estimated_cost} {self.status}>"
