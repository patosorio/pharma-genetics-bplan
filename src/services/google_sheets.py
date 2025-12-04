import os
import pandas as pd
from datetime import datetime, timedelta

from dotenv import load_dotenv

from sqlalchemy.orm import Session
from sqlalchemy.sql import func

from ..core.db import get_db
from ..core.googleapi.sheets_client import get_sheets_client
from ..core.shared.exceptions import ValidationError, ExternalServiceError
from google.api_core.exceptions import GoogleAPIError

from ..models.income import Income, IncomeStatus
from ..models.expenses import Expense, ExpenseType, ExpenseStatus as ExpStatus, ExpenseCategory
# from ..models.pending_investments import PendingInvestment

load_dotenv()

SHEET_ID = os.getenv('GOOGLE_SHEET_ID')

def fetch_sheet_range(service, range_name:str) -> pd.DataFrame:
    """Fetch and parse a sheet range to DataFrame."""
    try:
        result = service.spreadsheets().values().get(
            spreadsheetId=SHEET_ID, range=range_name
        ).execute()
        values = result.get('values', [])
        if not values:
            return pd.DataFrame()
        df = pd.DataFrame(values[1:], columns=values[0])
        
        # Data Cleaning
        numeric_cols = ['amount', 'vat', 'grand_total']
        for col in numeric_cols:
            if col in df:
                df[col] = pd.to_numeric(df[col].str.replace(',', ''), errors='coerce')
        date_cols = ['doc_date', 'overdue_date']
        for col in date_cols:
            if col in df:
                df[col] = pd.to_datetime(df[col], errors='coerce', dayfirst=True)
        return df
    except GoogleAPIError as e:
        raise ExternalServiceError(detail=f'Sheets API error: {str(e)}')


def get_or_create_category(db: Session, category: str | None, subcategory: str | None) -> int:
    """Dynamically create parent → child hierarchy from sheet values."""
    category = str(category or "Uncategorized").strip()
    subcategory = str(subcategory).strip() if pd.notna(subcategory) and subcategory else None

    # Parent category
    parent = db.query(ExpenseCategory).filter_by(name=category, parent_id=None).first()
    if not parent:
        parent = ExpenseCategory(name=category)
        db.add(parent)
        db.flush()

    # Subcategory (if present)
    if subcategory and subcategory.lower() != "nan":
        child = db.query(ExpenseCategory).filter_by(name=subcategory, parent_id=parent.id).first()
        if not child:
            child = ExpenseCategory(name=subcategory, parent_id=parent.id)
            db.add(child)
            db.flush()
        return child.id

    return parent.id


def _is_empty(val) -> bool:
    """Check if value is None, NaN, or empty string."""
    if val is None:
        return True
    if pd.isna(val):
        return True
    if isinstance(val, str) and val.strip() == "":
        return True
    return False


def _has_changes(existing, new_data: dict, compare_keys: list[str]) -> bool:
    """Check if any field differs between existing record and new data."""
    for key in compare_keys:
        if key not in new_data:
            continue
        existing_val = getattr(existing, key, None)
        new_val = new_data[key]
        # Normalize for comparison
        if hasattr(existing_val, 'value'):  # Enum
            existing_val = existing_val.value if existing_val else None
            new_val = new_val.value if hasattr(new_val, 'value') else new_val
        if isinstance(existing_val, (int, float)) and isinstance(new_val, (int, float)):
            if abs(float(existing_val) - float(new_val)) > 0.001:
                return True
        elif existing_val != new_val:
            return True
    return False


def sync_data(db: Session) -> dict:
    """Full sync from Google Sheets → DB with dynamic categories."""
    service = get_sheets_client()
    summary = {
        "income_inserted": 0, "income_updated": 0, "income_skipped": 0,
        "expenses_inserted": 0, "expenses_updated": 0, "expenses_skipped": 0,
    }

    # Income Sync
    income_df = fetch_sheet_range(service, "Income!A1:Z1000")
    income_compare_keys = ["doc_date", "customer", "currency", "amount", "vat", "grand_total", "status", "location"]
    
    for _, row in income_df.iterrows():
        row_id = row.get("row_id")
        raw_doc_no = row.get("doc_no")
        
        # Must have row_id to sync
        if _is_empty(row_id):
            continue
        
        row_id = str(row_id).strip()
        doc_no = raw_doc_no if not _is_empty(raw_doc_no) else f"AUTO-{row_id}"

        amount = float(row["amount"]) if pd.notna(row.get("amount")) else 0.0
        vat = float(row["vat"]) if pd.notna(row.get("vat")) else 0.0
        grand_total = float(row["grand_total"]) if pd.notna(row.get("grand_total")) else (amount + vat)

        income_data = {
            "row_id": row_id,
            "doc_no": doc_no,
            "doc_date": row["doc_date"].date() if pd.notna(row.get("doc_date")) else None,
            "customer": row.get("customer", "Unknown"),
            "currency": row.get("currency", "THB"),
            "amount": amount,
            "vat": vat,
            "grand_total": grand_total,
            "status": IncomeStatus[row["status"].upper()],
            "location": row.get("location", "Unknown").title(),
        }

        # Match by row_id (unique identifier from spreadsheet)
        existing = db.query(Income).filter_by(row_id=row_id).first()
        if existing:
            if _has_changes(existing, income_data, income_compare_keys):
                for k, v in income_data.items():
                    setattr(existing, k, v)
                existing.updated_at = datetime.utcnow()
                summary["income_updated"] += 1
            else:
                summary["income_skipped"] += 1
        else:
            db.add(Income(**income_data, created_at=datetime.utcnow()))
            summary["income_inserted"] += 1

    # Expenses Sync
    expenses_df = fetch_sheet_range(service, "Expenses!A1:Z10000")
    expense_compare_keys = ["doc_date", "overdue_date", "supplier", "currency", "amount", "vat", "grand_total", "status", "type", "location", "category_id"]
    
    for _, row in expenses_df.iterrows():
        row_id = row.get("row_id")
        raw_doc_no = row.get("doc_no")
        
        # Must have row_id to sync
        if _is_empty(row_id):
            continue
        
        row_id = str(row_id).strip()
        doc_no = raw_doc_no if not _is_empty(raw_doc_no) else f"AUTO-{row_id}"

        # Dynamic category
        category_id = get_or_create_category(db, row.get("category"), row.get("subcategory"))

        # Infer recurring from known patterns
        recurring_categories = {
            "Alquiler", "Utilidades", "Gastos Personal", "Sueldos",
            "Internet, Agua y Electricidad", "Electricidad Nave"
        }
        is_recurring = str(row.get("category", "")).strip() in recurring_categories

        amount = float(row["amount"]) if pd.notna(row.get("amount")) else 0.0
        vat = float(row["vat"]) if pd.notna(row.get("vat")) else 0.0
        grand_total = float(row["grand_total"]) if pd.notna(row.get("grand_total")) else (amount + vat)

        expense_data = {
            "row_id": row_id,
            "doc_no": doc_no,
            "doc_date": row["doc_date"].date() if pd.notna(row.get("doc_date")) else datetime.utcnow().date(),
            "overdue_date": row["overdue_date"].date() if pd.notna(row.get("overdue_date")) else None,
            "supplier": row.get("supplier", "Unknown"),
            "currency": row.get("currency", "THB"),
            "amount": amount,
            "vat": vat,
            "grand_total": grand_total,
            "status": ExpStatus[row["status"].upper()],
            "type": ExpenseType[row["type"]],
            "location": row.get("location", "Unknown").title(),
            "category_id": category_id,
            "is_recurring": is_recurring,
            "recurrence_period": "monthly" if is_recurring else None,
        }

        # Match by row_id (unique identifier from spreadsheet)
        existing = db.query(Expense).filter_by(row_id=row_id).first()
        if existing:
            if _has_changes(existing, expense_data, expense_compare_keys):
                for k, v in expense_data.items():
                    setattr(existing, k, v)
                existing.updated_at = datetime.utcnow()
                summary["expenses_updated"] += 1
            else:
                summary["expenses_skipped"] += 1
        else:
            db.add(Expense(**expense_data, created_at=datetime.utcnow()))
            summary["expenses_inserted"] += 1

    db.commit()

    # Quick financial summary
    total_income = db.query(func.sum(Income.grand_total)).scalar() or 0
    total_expenses = db.query(func.sum(Expense.grand_total)).scalar() or 0
    summary.update({
        "total_income_thb": float(total_income),
        "total_expenses_thb": float(total_expenses),
        "net_position_thb": float(total_income - total_expenses),
        "status": "sync_complete",
        "timestamp": datetime.utcnow().isoformat(),
    })

    return summary