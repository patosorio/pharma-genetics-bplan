"""
Cashflow Report Service

This service generates cashflow reports with the following structure:
- Cash Inflows (Sales income with VAT, Fundings, Other income)
- Cash Outflows (COGS, OPEX, CAPEX - all by category/subcategory)
- Net Cashflow
- Opening Cash Balance
- Closing Cash Balance

Supports two formats:
- yearly: Single total column
- monthly: Column per month

Note: Uses grand_total (including VAT) for all amounts
"""

from datetime import datetime, date
from typing import Optional, Dict, List, Any
from decimal import Decimal
from sqlalchemy.orm import Session
from sqlalchemy import func
import pandas as pd
import numpy as np

from ...models.income import Income
from ...models.expenses import Expense, ExpenseCategory, ExpenseType
from ...core.shared.exceptions import ValidationError


class CashflowService:
    """Service for generating Cashflow reports."""
    
    def __init__(self, db: Session):
        """
        Initialize Cashflow service.
        
        Args:
            db: Database session
        """
        self.db = db
    
    @staticmethod
    def validate_date_range(start_date: date, end_date: date) -> None:
        """
        Validate date range (max 12 months).
        
        Args:
            start_date: Start date
            end_date: End date
            
        Raises:
            ValidationError: If date range exceeds 12 months
        """
        if start_date > end_date:
            raise ValidationError(
                detail="start_date cannot be after end_date",
                context={
                    "start_date": start_date.isoformat(),
                    "end_date": end_date.isoformat()
                }
            )
        
        # Calculate months difference
        months_diff = (end_date.year - start_date.year) * 12 + (end_date.month - start_date.month)
        
        if months_diff > 12:
            raise ValidationError(
                detail="Date range cannot exceed 12 months",
                context={
                    "start_date": start_date.isoformat(),
                    "end_date": end_date.isoformat(),
                    "months_difference": months_diff,
                    "max_allowed_months": 12
                }
            )
    
    def get_income_data(
        self,
        start_date: date,
        end_date: date,
        location: Optional[str] = None
    ) -> pd.DataFrame:
        """
        Fetch income data from database (sales income with VAT).
        
        Args:
            start_date: Start date for filtering
            end_date: End date for filtering
            location: Optional location filter
            
        Returns:
            DataFrame with income records (using grand_total including VAT)
        """
        query = self.db.query(
            Income.doc_date,
            Income.grand_total,  # Total including VAT for cashflow
            Income.location
        ).filter(
            Income.doc_date >= start_date,
            Income.doc_date <= end_date
        )
        
        if location:
            query = query.filter(Income.location == location)
        
        results = query.all()
        
        if not results:
            return pd.DataFrame(columns=['doc_date', 'grand_total', 'location'])
        
        df = pd.DataFrame(results, columns=['doc_date', 'grand_total', 'location'])
        df['grand_total'] = df['grand_total'].astype(float)
        return df
    
    def get_expense_data(
        self,
        start_date: date,
        end_date: date,
        location: Optional[str] = None,
        expense_types: Optional[List[ExpenseType]] = None
    ) -> pd.DataFrame:
        """
        Fetch expense data from database with category information.
        
        Args:
            start_date: Start date for filtering
            end_date: End date for filtering
            location: Optional location filter
            expense_types: List of expense types to include
            
        Returns:
            DataFrame with expense records including category hierarchy (using grand_total with VAT)
        """
        query = self.db.query(
            Expense.doc_date,
            Expense.grand_total,  # Total including VAT for cashflow
            Expense.type,
            Expense.location,
            Expense.category_id,
            ExpenseCategory.name.label('category_name'),
            ExpenseCategory.parent_id
        ).join(
            ExpenseCategory,
            Expense.category_id == ExpenseCategory.id
        ).filter(
            Expense.doc_date >= start_date,
            Expense.doc_date <= end_date
        )
        
        if location:
            query = query.filter(Expense.location == location)
        
        if expense_types:
            query = query.filter(Expense.type.in_(expense_types))
        
        results = query.all()
        
        if not results:
            return pd.DataFrame(columns=[
                'doc_date', 'grand_total', 'type', 'location',
                'category_id', 'category_name', 'parent_id'
            ])
        
        df = pd.DataFrame(results, columns=[
            'doc_date', 'grand_total', 'type', 'location',
            'category_id', 'category_name', 'parent_id'
        ])
        df['grand_total'] = df['grand_total'].astype(float)
        
        # Get parent category names for subcategories
        category_map = {}
        categories = self.db.query(ExpenseCategory).all()
        for cat in categories:
            category_map[cat.id] = {
                'name': cat.name,
                'parent_id': cat.parent_id
            }
        
        # Add parent category name
        df['parent_category'] = df.apply(
            lambda row: category_map[row['parent_id']]['name'] 
            if pd.notna(row['parent_id']) and row['parent_id'] in category_map 
            else None,
            axis=1
        )
        
        # Determine if it's a parent or child category
        df['is_subcategory'] = df['parent_id'].notna()
        
        return df
    
    def generate_monthly_periods(self, start_date: date, end_date: date) -> List[str]:
        """
        Generate list of month periods between start and end date.
        
        Args:
            start_date: Start date
            end_date: End date
            
        Returns:
            List of period strings in format 'mmm-yy' (e.g., 'sep-24')
        """
        periods = []
        current = start_date.replace(day=1)
        end = end_date.replace(day=1)
        
        while current <= end:
            period_str = current.strftime('%b-%y').lower()
            periods.append(period_str)
            
            # Move to next month
            if current.month == 12:
                current = current.replace(year=current.year + 1, month=1)
            else:
                current = current.replace(month=current.month + 1)
        
        return periods
    
    def assign_period(self, doc_date: date, format_type: str, periods: List[str]) -> str:
        """
        Assign a document date to a period.
        
        Args:
            doc_date: Document date
            format_type: 'yearly' or 'monthly'
            periods: List of period strings
            
        Returns:
            Period string
        """
        if format_type == 'yearly':
            return 'Total'
        else:  # monthly
            return doc_date.strftime('%b-%y').lower()
    
    def build_inflows_section(
        self,
        income_df: pd.DataFrame,
        format_type: str,
        periods: List[str]
    ) -> Dict[str, Any]:
        """
        Build cash inflows section.
        
        Args:
            income_df: Income DataFrame
            format_type: 'yearly' or 'monthly'
            periods: List of periods
            
        Returns:
            Dictionary with inflows data
        """
        if income_df.empty:
            sales_income = {period: 0.0 for period in periods}
        else:
            # Assign periods to income records
            income_df['period'] = income_df['doc_date'].apply(
                lambda x: self.assign_period(x, format_type, periods)
            )
            
            # Calculate sales income per period (with VAT)
            sales_income = income_df.groupby('period')['grand_total'].sum().to_dict()
            sales_income = {period: sales_income.get(period, 0.0) for period in periods}
        
        # Fundings - empty for now
        fundings = {period: 0.0 for period in periods}
        
        # Other income - empty for now
        other_income = {period: 0.0 for period in periods}
        
        # Total inflows
        total_inflows = {
            period: sales_income[period] + fundings[period] + other_income[period]
            for period in periods
        }
        
        return {
            'sales_income': sales_income,
            'fundings': fundings,
            'other_income': other_income,
            'total_inflows': total_inflows
        }
    
    def build_outflows_section(
        self,
        expense_df: pd.DataFrame,
        format_type: str,
        periods: List[str],
        section_name: str
    ) -> Dict[str, Any]:
        """
        Build expense outflows section (COGS, OPEX, or CAPEX) grouped by category/subcategory.
        
        Args:
            expense_df: Expense DataFrame
            format_type: 'yearly' or 'monthly'
            periods: List of periods
            section_name: Name of the section ('COGS', 'OPEX', or 'CAPEX')
            
        Returns:
            Dictionary with expense data by category
        """
        if expense_df.empty:
            return {
                'expenses_by_category': {},
                'total': {period: 0.0 for period in periods}
            }
        
        # Assign periods
        expense_df['period'] = expense_df['doc_date'].apply(
            lambda x: self.assign_period(x, format_type, periods)
        )
        
        # Build hierarchical structure
        expenses_by_category = {}
        
        # Get all unique parent categories from the parent_category column
        parent_categories = expense_df[expense_df['parent_category'].notna()]['parent_category'].unique()
        
        for parent_cat in parent_categories:
            # Get all subcategories under this parent
            subcategories = expense_df[
                (expense_df['parent_category'] == parent_cat) & 
                (expense_df['is_subcategory'])
            ]['category_name'].unique()
            
            category_data = {'subcategories': {}}
            
            # Add subcategories with their totals
            for subcat in subcategories:
                subcat_expenses = expense_df[
                    (expense_df['category_name'] == subcat) & 
                    (expense_df['parent_category'] == parent_cat)
                ]
                period_totals = subcat_expenses.groupby('period')['grand_total'].sum().to_dict()
                category_data['subcategories'][subcat] = {
                    period: period_totals.get(period, 0.0) for period in periods
                }
            
            # Check if there are any direct expenses on the parent category
            parent_direct_expenses = expense_df[
                (expense_df['category_name'] == parent_cat) & 
                (~expense_df['is_subcategory'])
            ]
            
            if not parent_direct_expenses.empty:
                period_totals = parent_direct_expenses.groupby('period')['grand_total'].sum().to_dict()
                category_data['direct'] = {
                    period: period_totals.get(period, 0.0) for period in periods
                }
            
            expenses_by_category[parent_cat] = category_data
        
        # Also handle categories without parent (if any)
        orphan_categories = expense_df[~expense_df['is_subcategory']]['category_name'].unique()
        for orphan_cat in orphan_categories:
            # Skip if already processed as a parent
            if orphan_cat not in [cat for cats in expense_df['parent_category'].dropna().unique() for cat in [cats]]:
                orphan_expenses = expense_df[expense_df['category_name'] == orphan_cat]
                period_totals = orphan_expenses.groupby('period')['grand_total'].sum().to_dict()
                expenses_by_category[orphan_cat] = {
                    'direct': {period: period_totals.get(period, 0.0) for period in periods},
                    'subcategories': {}
                }
        
        # Calculate total per period
        total = expense_df.groupby('period')['grand_total'].sum().to_dict()
        total = {period: total.get(period, 0.0) for period in periods}
        
        return {
            'expenses_by_category': expenses_by_category,
            'total': total
        }
    
    def generate_cashflow_report(
        self,
        start_date: date,
        end_date: date,
        format_type: str = 'yearly',
        location: Optional[str] = None,
        opening_balance: float = 0.0
    ) -> Dict[str, Any]:
        """
        Generate complete cashflow report.
        
        Args:
            start_date: Start date for report
            end_date: End date for report
            format_type: 'yearly' or 'monthly'
            location: Optional location filter ('All' for all locations)
            opening_balance: Opening cash balance (default: 0.0)
            
        Returns:
            Dictionary containing complete cashflow report
        """
        # Validate date range
        self.validate_date_range(start_date, end_date)
        
        # Validate format
        if format_type not in ['yearly', 'monthly']:
            raise ValidationError(
                detail="Invalid format. Must be 'yearly' or 'monthly'",
                context={'provided_format': format_type}
            )
        
        # Handle location filter
        location_filter = None if location == 'All' else location
        
        # Generate periods
        if format_type == 'yearly':
            periods = ['Total']
        else:
            periods = self.generate_monthly_periods(start_date, end_date)
        
        # Fetch data
        income_df = self.get_income_data(start_date, end_date, location_filter)
        cogs_df = self.get_expense_data(
            start_date, end_date, location_filter, [ExpenseType.COGS]
        )
        opex_df = self.get_expense_data(
            start_date, end_date, location_filter, [ExpenseType.OPEX]
        )
        capex_df = self.get_expense_data(
            start_date, end_date, location_filter, [ExpenseType.CAPEX]
        )
        
        # Build sections
        inflows = self.build_inflows_section(income_df, format_type, periods)
        cogs_section = self.build_outflows_section(cogs_df, format_type, periods, 'COGS')
        opex_section = self.build_outflows_section(opex_df, format_type, periods, 'OPEX')
        capex_section = self.build_outflows_section(capex_df, format_type, periods, 'CAPEX')
        
        # Calculate totals
        total_inflows = inflows['total_inflows']
        total_cogs = cogs_section['total']
        total_opex = opex_section['total']
        total_capex = capex_section['total']
        
        # Total outflows = COGS + OPEX + CAPEX
        total_outflows = {
            period: (
                total_cogs.get(period, 0.0) + 
                total_opex.get(period, 0.0) + 
                total_capex.get(period, 0.0)
            )
            for period in periods
        }
        
        # Net cashflow = Inflows - Outflows
        net_cashflow = {
            period: total_inflows.get(period, 0.0) - total_outflows.get(period, 0.0)
            for period in periods
        }
        
        # Calculate opening and closing balances
        if format_type == 'yearly':
            opening_balance_dict = {'Total': opening_balance}
            closing_balance_dict = {
                'Total': opening_balance + net_cashflow.get('Total', 0.0)
            }
        else:
            # For monthly, calculate cumulative balances
            opening_balance_dict = {}
            closing_balance_dict = {}
            cumulative_balance = opening_balance
            
            for period in periods:
                opening_balance_dict[period] = cumulative_balance
                cumulative_balance += net_cashflow.get(period, 0.0)
                closing_balance_dict[period] = cumulative_balance
        
        return {
            'report_info': {
                'start_date': start_date.isoformat(),
                'end_date': end_date.isoformat(),
                'format': format_type,
                'location': location or 'All',
                'periods': periods,
                'generated_at': datetime.utcnow().isoformat()
            },
            'cash_inflows': inflows,
            'cash_outflows': {
                'cogs': cogs_section,
                'opex': opex_section,
                'capex': capex_section,
                'total_outflows': total_outflows
            },
            'net_cashflow': net_cashflow,
            'opening_balance': opening_balance_dict,
            'closing_balance': closing_balance_dict
        }
