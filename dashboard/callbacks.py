"""Dashboard callbacks for interactivity."""

import requests
from dash import Input, Output, State, html, dash_table, dcc
from dash.exceptions import PreventUpdate
import pandas as pd
from datetime import datetime
import plotly.graph_objects as go
import plotly.express as px
from dashboard.app import dash_app

# API base URL
API_BASE_URL = "http://localhost:8000/api/v1"

def format_currency(value):
    """Format number as currency."""
    try:
        return f"฿{float(value):,.2f}"
    except (ValueError, TypeError):
        return str(value)

def format_date_for_api(date_str):
    """Convert YYYY-MM-DD to DD/MM/YYYY for API."""
    if not date_str:
        return None
    try:
        dt = datetime.strptime(date_str, "%Y-%m-%d")
        return dt.strftime("%d/%m/%Y")
    except:
        return date_str

# Toggle sidebar
@dash_app.callback(
    [Output("sidebar", "className"),
     Output("content", "className")],
    [Input("toggle-sidebar", "n_clicks")],
    [State("sidebar", "className")]
)
def toggle_sidebar(n_clicks, current_class):
    if n_clicks % 2 == 1:
        return "collapsed", "expanded"
    return "", ""

# Navigation callbacks
@dash_app.callback(
    [Output("active-tab", "data"),
     Output("nav-expenses", "active"),
     Output("nav-expenses-report", "active"),
     Output("nav-income", "active"),
     Output("nav-pnl", "active"),
     Output("nav-cashflow", "active")],
    [Input("nav-expenses", "n_clicks"),
     Input("nav-expenses-report", "n_clicks"),
     Input("nav-income", "n_clicks"),
     Input("nav-pnl", "n_clicks"),
     Input("nav-cashflow", "n_clicks")],
    [State("active-tab", "data")]
)
def handle_navigation(exp_clicks, exp_report_clicks, inc_clicks, pnl_clicks, cf_clicks, current_tab):
    from dash import ctx
    
    if not ctx.triggered:
        return "expenses", True, False, False, False, False
    
    button_id = ctx.triggered[0]["prop_id"].split(".")[0]
    
    if button_id == "nav-expenses":
        return "expenses", True, False, False, False, False
    elif button_id == "nav-expenses-report":
        return "expenses-report", False, True, False, False, False
    elif button_id == "nav-income":
        return "income", False, False, True, False, False
    elif button_id == "nav-pnl":
        return "pnl", False, False, False, True, False
    elif button_id == "nav-cashflow":
        return "cashflow", False, False, False, False, True
    
    return (current_tab, 
            current_tab == "expenses", 
            current_tab == "expenses-report",
            current_tab == "income", 
            current_tab == "pnl", 
            current_tab == "cashflow")

# Update tab content based on active tab
@dash_app.callback(
    Output("tab-content", "children"),
    [Input("active-tab", "data")]
)
def update_tab_content(active_tab):
    from dashboard.layout import create_expenses_tab, create_expenses_report_tab, create_income_tab, create_pnl_tab, create_cashflow_tab
    
    if active_tab == "expenses":
        return create_expenses_tab()
    elif active_tab == "expenses-report":
        return create_expenses_report_tab()
    elif active_tab == "income":
        return create_income_tab()
    elif active_tab == "pnl":
        return create_pnl_tab()
    elif active_tab == "cashflow":
        return create_cashflow_tab()
    
    return html.Div("Select a tab")

# Expenses callback
@dash_app.callback(
    Output("expenses-content", "children"),
    [Input("apply-filters", "n_clicks"),
     Input("active-tab", "data")],
    [State("location-filter", "value"),
     State("start-date-filter", "date"),
     State("end-date-filter", "date")]
)
def update_expenses(n_clicks, active_tab, location, start_date, end_date):
    if active_tab != "expenses":
        raise PreventUpdate
    
    try:
        # Build API URL with filters
        params = {}
        if start_date:
            params["start_date"] = format_date_for_api(start_date)
        if end_date:
            params["end_date"] = format_date_for_api(end_date)
        if location and location != "All":
            params["location"] = location
        
        response = requests.get(f"{API_BASE_URL}/expenses", params=params)
        response.raise_for_status()
        data = response.json()
        
        if not data.get("expenses"):
            return html.Div("No expenses found for the selected filters.", className="info-text")
        
        # Convert to DataFrame
        df = pd.DataFrame(data["expenses"])
        
        # Select and format columns
        display_columns = ["doc_no", "doc_date", "supplier", "type", "location", "amount", "vat", "grand_total", "status"]
        df = df[display_columns]
        
        # Format currency columns
        for col in ["amount", "vat", "grand_total"]:
            df[col] = df[col].apply(lambda x: float(x) if pd.notna(x) else 0)
        
        # Create DataTable
        table = dash_table.DataTable(
            data=df.to_dict('records'),
            columns=[
                {"name": "Doc No", "id": "doc_no"},
                {"name": "Date", "id": "doc_date"},
                {"name": "Supplier", "id": "supplier"},
                {"name": "Type", "id": "type"},
                {"name": "Location", "id": "location"},
                {"name": "Amount", "id": "amount", "type": "numeric", "format": {"specifier": ",.2f"}},
                {"name": "VAT", "id": "vat", "type": "numeric", "format": {"specifier": ",.2f"}},
                {"name": "Total", "id": "grand_total", "type": "numeric", "format": {"specifier": ",.2f"}},
                {"name": "Status", "id": "status"},
            ],
            style_table={'overflowX': 'auto'},
            style_cell={
                'textAlign': 'left',
                'padding': '8px',
                'fontFamily': 'Helvetica Neue Light, Helvetica Neue, Helvetica, Arial, sans-serif',
                'fontSize': '10pt',
                'color': '#000000',
            },
            style_header={
                'backgroundColor': '#f5f5f2',
                'fontWeight': '500',
                'fontFamily': 'Helvetica Neue, Helvetica, Arial, sans-serif',
                'fontSize': '12pt',
                'color': '#000000',
                'borderBottom': '2px solid #d4d4cd',
            },
            style_data={
                'borderBottom': '1px solid #e8e8e3',
            },
            style_data_conditional=[
                {
                    'if': {'row_index': 'odd'},
                    'backgroundColor': '#fafaf8',
                }
            ],
            page_size=20,
        )
        
        return html.Div([
            html.P(f"Total expenses: {data['total']}", className="info-text mb-3"),
            table
        ])
        
    except Exception as e:
        return html.Div(f"Error loading expenses: {str(e)}", style={"color": "#a65d57"})

# Income callback
@dash_app.callback(
    Output("income-content", "children"),
    [Input("apply-filters", "n_clicks"),
     Input("active-tab", "data")],
    [State("location-filter", "value"),
     State("start-date-filter", "date"),
     State("end-date-filter", "date")]
)
def update_income(n_clicks, active_tab, location, start_date, end_date):
    if active_tab != "income":
        raise PreventUpdate
    
    try:
        # Build API URL with filters
        params = {}
        if start_date:
            params["start_date"] = format_date_for_api(start_date)
        if end_date:
            params["end_date"] = format_date_for_api(end_date)
        if location and location != "All":
            params["location"] = location
        
        response = requests.get(f"{API_BASE_URL}/income", params=params)
        response.raise_for_status()
        data = response.json()
        
        if not data.get("income"):
            return html.Div("No income records found for the selected filters.", className="info-text")
        
        # Convert to DataFrame
        df = pd.DataFrame(data["income"])
        
        # Select and format columns
        display_columns = ["doc_no", "doc_date", "customer", "location", "amount", "vat", "grand_total", "status"]
        df = df[display_columns]
        
        # Format currency columns
        for col in ["amount", "vat", "grand_total"]:
            df[col] = df[col].apply(lambda x: float(x) if pd.notna(x) else 0)
        
        # Create DataTable
        table = dash_table.DataTable(
            data=df.to_dict('records'),
            columns=[
                {"name": "Doc No", "id": "doc_no"},
                {"name": "Date", "id": "doc_date"},
                {"name": "Customer", "id": "customer"},
                {"name": "Location", "id": "location"},
                {"name": "Amount", "id": "amount", "type": "numeric", "format": {"specifier": ",.2f"}},
                {"name": "VAT", "id": "vat", "type": "numeric", "format": {"specifier": ",.2f"}},
                {"name": "Total", "id": "grand_total", "type": "numeric", "format": {"specifier": ",.2f"}},
                {"name": "Status", "id": "status"},
            ],
            style_table={'overflowX': 'auto'},
            style_cell={
                'textAlign': 'left',
                'padding': '8px',
                'fontFamily': 'Helvetica Neue Light, Helvetica Neue, Helvetica, Arial, sans-serif',
                'fontSize': '10pt',
                'color': '#000000',
            },
            style_header={
                'backgroundColor': '#f5f5f2',
                'fontWeight': '500',
                'fontFamily': 'Helvetica Neue, Helvetica, Arial, sans-serif',
                'fontSize': '12pt',
                'color': '#000000',
                'borderBottom': '2px solid #d4d4cd',
            },
            style_data={
                'borderBottom': '1px solid #e8e8e3',
            },
            style_data_conditional=[
                {
                    'if': {'row_index': 'odd'},
                    'backgroundColor': '#fafaf8',
                }
            ],
            page_size=20,
        )
        
        return html.Div([
            html.P(f"Total income records: {data['total']}", className="info-text mb-3"),
            table
        ])
        
    except Exception as e:
        return html.Div(f"Error loading income: {str(e)}", style={"color": "#a65d57"})

# P&L callback
@dash_app.callback(
    Output("pnl-content", "children"),
    [Input("apply-filters", "n_clicks"),
     Input("active-tab", "data")],
    [State("location-filter", "value"),
     State("start-date-filter", "date"),
     State("end-date-filter", "date"),
     State("format-filter", "value")]
)
def update_pnl(n_clicks, active_tab, location, start_date, end_date, format_type):
    if active_tab != "pnl":
        raise PreventUpdate
    
    try:
        # Build API URL with filters
        params = {
            "start_date": format_date_for_api(start_date) or "01/01/2024",
            "end_date": format_date_for_api(end_date) or "31/12/2024",
            "format": format_type or "yearly",
        }
        if location and location != "All":
            params["location"] = location
        
        response = requests.get(f"{API_BASE_URL}/reports/pnl", params=params)
        response.raise_for_status()
        data = response.json()
        
        # Build P&L table
        periods = data["report_info"]["periods"]
        rows = []
        
        # Revenue section
        rows.append({"item": "REVENUE", **{p: "" for p in periods}, "is_header": True})
        for customer, values in data["revenue"]["revenue_by_customer"].items():
            rows.append({"item": f"  {customer}", **values, "is_subitem": True})
        rows.append({"item": "Total Revenue", **data["revenue"]["total_net_revenue"], "is_total": True})
        
        # COGS section
        rows.append({"item": "", **{p: "" for p in periods}})
        rows.append({"item": "COST OF GOODS SOLD", **{p: "" for p in periods}, "is_header": True})
        if "expenses_by_category" in data["cogs"]:
            for category, cat_data in data["cogs"]["expenses_by_category"].items():
                rows.append({"item": f"  {category}", **{p: "" for p in periods}, "is_subheader": True})
                if "subcategories" in cat_data:
                    for subcat, values in cat_data["subcategories"].items():
                        rows.append({"item": f"    {subcat}", **values, "is_subitem": True})
        rows.append({"item": "Total COGS", **data["cogs"]["total"], "is_total": True})
        
        # Gross Profit
        rows.append({"item": "", **{p: "" for p in periods}})
        rows.append({"item": "GROSS PROFIT", **data["gross_profit"], "is_total": True})
        
        # OPEX section
        rows.append({"item": "", **{p: "" for p in periods}})
        rows.append({"item": "OPERATING EXPENSES", **{p: "" for p in periods}, "is_header": True})
        if "expenses_by_category" in data["operating_expenses"]:
            for category, cat_data in data["operating_expenses"]["expenses_by_category"].items():
                rows.append({"item": f"  {category}", **{p: "" for p in periods}, "is_subheader": True})
                if "subcategories" in cat_data:
                    for subcat, values in cat_data["subcategories"].items():
                        rows.append({"item": f"    {subcat}", **values, "is_subitem": True})
                if "direct" in cat_data:
                    rows.append({"item": f"    Direct", **cat_data["direct"], "is_subitem": True})
        rows.append({"item": "Total OPEX", **data["operating_expenses"]["total"], "is_total": True})
        
        # Bottom line
        rows.append({"item": "", **{p: "" for p in periods}})
        rows.append({"item": "EBIT", **data["ebit"], "is_total": True})
        rows.append({"item": "Income Tax (15%)", **data["income_tax"], "is_subitem": True})
        rows.append({"item": "NET EARNINGS", **data["net_earnings"], "is_total": True, "is_final": True})
        
        # Convert to DataFrame
        df = pd.DataFrame(rows)
        
        # Format numbers
        for period in periods:
            if period in df.columns:
                df[period] = df[period].apply(lambda x: f"{float(x):,.2f}" if x != "" and pd.notna(x) else "")
        
        # Style conditionals
        style_conditions = [
            {
                'if': {'filter_query': '{is_header} = true'},
                'fontWeight': '600',
                'backgroundColor': '#e8e8e3',
                'fontSize': '12pt',
            },
            {
                'if': {'filter_query': '{is_subheader} = true'},
                'fontWeight': '500',
                'fontStyle': 'italic',
            },
            {
                'if': {'filter_query': '{is_total} = true'},
                'fontWeight': '600',
                'borderTop': '2px solid #4a4a45',
            },
            {
                'if': {'filter_query': '{is_final} = true'},
                'fontWeight': '700',
                'backgroundColor': '#f5f5f2',
                'borderTop': '3px double #4a4a45',
            },
        ]
        
        # Remove helper columns
        display_df = df[["item"] + periods]
        
        # Create columns definition
        columns = [{"name": "Item", "id": "item"}]
        for period in periods:
            columns.append({"name": period, "id": period})
        
        table = dash_table.DataTable(
            data=display_df.to_dict('records'),
            columns=columns,
            style_table={'overflowX': 'auto'},
            style_cell={
                'textAlign': 'left',
                'padding': '8px',
                'fontFamily': 'Helvetica Neue Light, Helvetica Neue, Helvetica, Arial, sans-serif',
                'fontSize': '10pt',
                'color': '#000000',
            },
            style_cell_conditional=[
                {
                    'if': {'column_id': 'item'},
                    'width': '300px',
                },
                {
                    'if': {'column_id': periods},
                    'textAlign': 'right',
                }
            ],
            style_header={
                'backgroundColor': '#f5f5f2',
                'fontWeight': '500',
                'fontFamily': 'Helvetica Neue, Helvetica, Arial, sans-serif',
                'fontSize': '12pt',
                'color': '#000000',
                'borderBottom': '2px solid #d4d4cd',
            },
            style_data={
                'borderBottom': '1px solid #e8e8e3',
            },
            style_data_conditional=style_conditions,
        )
        
        return html.Div([
            html.P(
                f"P&L Report: {data['report_info']['start_date']} to {data['report_info']['end_date']} | "
                f"Format: {format_type.title()} | Location: {location or 'All'}",
                className="info-text mb-3"
            ),
            table
        ])
        
    except Exception as e:
        return html.Div(f"Error loading P&L: {str(e)}", style={"color": "#a65d57"})

# Cashflow callback
@dash_app.callback(
    Output("cashflow-content", "children"),
    [Input("apply-filters", "n_clicks"),
     Input("active-tab", "data")],
    [State("location-filter", "value"),
     State("start-date-filter", "date"),
     State("end-date-filter", "date"),
     State("format-filter", "value"),
     State("opening-balance", "value")]
)
def update_cashflow(n_clicks, active_tab, location, start_date, end_date, format_type, opening_balance):
    if active_tab != "cashflow":
        raise PreventUpdate
    
    try:
        # Build API URL with filters
        params = {
            "start_date": format_date_for_api(start_date) or "01/01/2024",
            "end_date": format_date_for_api(end_date) or "31/12/2024",
            "format": format_type or "yearly",
            "opening_balance": opening_balance or 0.0,
        }
        if location and location != "All":
            params["location"] = location
        
        response = requests.get(f"{API_BASE_URL}/reports/cashflow", params=params)
        response.raise_for_status()
        data = response.json()
        
        # Build Cashflow table
        periods = data["report_info"]["periods"]
        rows = []
        
        # Opening Balance
        rows.append({"item": "OPENING BALANCE", **data["opening_balance"], "is_header": True})
        rows.append({"item": "", **{p: "" for p in periods}})
        
        # Cash Inflows
        rows.append({"item": "CASH INFLOWS", **{p: "" for p in periods}, "is_header": True})
        rows.append({"item": "  Sales Income", **data["cash_inflows"]["sales_income"], "is_subitem": True})
        rows.append({"item": "  Fundings", **data["cash_inflows"]["fundings"], "is_subitem": True})
        rows.append({"item": "  Other Income", **data["cash_inflows"]["other_income"], "is_subitem": True})
        rows.append({"item": "Total Inflows", **data["cash_inflows"]["total_inflows"], "is_total": True})
        
        # Cash Outflows
        rows.append({"item": "", **{p: "" for p in periods}})
        rows.append({"item": "CASH OUTFLOWS", **{p: "" for p in periods}, "is_header": True})
        
        # COGS
        rows.append({"item": "  Cost of Goods Sold", **{p: "" for p in periods}, "is_subheader": True})
        if "expenses_by_category" in data["cash_outflows"]["cogs"]:
            for category, cat_data in data["cash_outflows"]["cogs"]["expenses_by_category"].items():
                if "subcategories" in cat_data:
                    for subcat, values in cat_data["subcategories"].items():
                        rows.append({"item": f"    {subcat}", **values, "is_subitem": True})
        rows.append({"item": "  Total COGS", **data["cash_outflows"]["cogs"]["total"], "is_subitem": True})
        
        # OPEX
        rows.append({"item": "  Operating Expenses", **{p: "" for p in periods}, "is_subheader": True})
        if "expenses_by_category" in data["cash_outflows"]["opex"]:
            for category, cat_data in data["cash_outflows"]["opex"]["expenses_by_category"].items():
                if "subcategories" in cat_data:
                    for subcat, values in cat_data["subcategories"].items():
                        rows.append({"item": f"    {subcat}", **values, "is_subitem": True})
        rows.append({"item": "  Total OPEX", **data["cash_outflows"]["opex"]["total"], "is_subitem": True})
        
        # CAPEX
        rows.append({"item": "  Capital Expenses", **{p: "" for p in periods}, "is_subheader": True})
        if "expenses_by_category" in data["cash_outflows"]["capex"]:
            for category, cat_data in data["cash_outflows"]["capex"]["expenses_by_category"].items():
                if "subcategories" in cat_data:
                    for subcat, values in cat_data["subcategories"].items():
                        rows.append({"item": f"    {subcat}", **values, "is_subitem": True})
        rows.append({"item": "  Total CAPEX", **data["cash_outflows"]["capex"]["total"], "is_subitem": True})
        
        rows.append({"item": "Total Outflows", **data["cash_outflows"]["total_outflows"], "is_total": True})
        
        # Net Cashflow and Closing Balance
        rows.append({"item": "", **{p: "" for p in periods}})
        rows.append({"item": "NET CASHFLOW", **data["net_cashflow"], "is_total": True})
        rows.append({"item": "CLOSING BALANCE", **data["closing_balance"], "is_total": True, "is_final": True})
        
        # Convert to DataFrame
        df = pd.DataFrame(rows)
        
        # Format numbers
        for period in periods:
            if period in df.columns:
                df[period] = df[period].apply(lambda x: f"{float(x):,.2f}" if x != "" and pd.notna(x) else "")
        
        # Style conditionals
        style_conditions = [
            {
                'if': {'filter_query': '{is_header} = true'},
                'fontWeight': '600',
                'backgroundColor': '#e8e8e3',
                'fontSize': '12pt',
            },
            {
                'if': {'filter_query': '{is_subheader} = true'},
                'fontWeight': '500',
                'fontStyle': 'italic',
            },
            {
                'if': {'filter_query': '{is_total} = true'},
                'fontWeight': '600',
                'borderTop': '2px solid #4a4a45',
            },
            {
                'if': {'filter_query': '{is_final} = true'},
                'fontWeight': '700',
                'backgroundColor': '#f5f5f2',
                'borderTop': '3px double #4a4a45',
            },
        ]
        
        # Remove helper columns
        display_df = df[["item"] + periods]
        
        # Create columns definition
        columns = [{"name": "Item", "id": "item"}]
        for period in periods:
            columns.append({"name": period, "id": period})
        
        table = dash_table.DataTable(
            data=display_df.to_dict('records'),
            columns=columns,
            style_table={'overflowX': 'auto'},
            style_cell={
                'textAlign': 'left',
                'padding': '8px',
                'fontFamily': 'Helvetica Neue Light, Helvetica Neue, Helvetica, Arial, sans-serif',
                'fontSize': '10pt',
                'color': '#000000',
            },
            style_cell_conditional=[
                {
                    'if': {'column_id': 'item'},
                    'width': '300px',
                },
                {
                    'if': {'column_id': periods},
                    'textAlign': 'right',
                }
            ],
            style_header={
                'backgroundColor': '#f5f5f2',
                'fontWeight': '500',
                'fontFamily': 'Helvetica Neue, Helvetica, Arial, sans-serif',
                'fontSize': '12pt',
                'color': '#000000',
                'borderBottom': '2px solid #d4d4cd',
            },
            style_data={
                'borderBottom': '1px solid #e8e8e3',
            },
            style_data_conditional=style_conditions,
        )
        
        return html.Div([
            html.P(
                f"Cashflow Report: {data['report_info']['start_date']} to {data['report_info']['end_date']} | "
                f"Format: {format_type.title()} | Location: {location or 'All'}",
                className="info-text mb-3"
            ),
            table
        ])
        
    except Exception as e:
        return html.Div(f"Error loading Cashflow: {str(e)}", style={"color": "#a65d57"})

# Expenses Report callback
@dash_app.callback(
    Output("expenses-report-content", "children"),
    [Input("apply-filters", "n_clicks"),
     Input("active-tab", "data")],
    [State("location-filter", "value"),
     State("start-date-filter", "date"),
     State("end-date-filter", "date")]
)
def update_expenses_report(n_clicks, active_tab, location, start_date, end_date):
    if active_tab != "expenses-report":
        raise PreventUpdate
    
    try:
        # Build API URL with filters
        params = {}
        if start_date:
            params["start_date"] = format_date_for_api(start_date)
        if end_date:
            params["end_date"] = format_date_for_api(end_date)
        if location and location != "All":
            params["location"] = location
        
        response = requests.get(f"{API_BASE_URL}/expenses", params=params)
        response.raise_for_status()
        data = response.json()
        
        if not data.get("expenses"):
            return html.Div("No expenses found for the selected filters.", className="info-text")
        
        # Convert to DataFrame
        df = pd.DataFrame(data["expenses"])
        df['doc_date'] = pd.to_datetime(df['doc_date'])
        df['grand_total'] = df['grand_total'].astype(float)
        
        # Sort by date
        df = df.sort_values('doc_date')
        
        # Group by type and date for line chart
        df['month'] = df['doc_date'].dt.to_period('M').astype(str)
        monthly_by_type = df.groupby(['month', 'type'])['grand_total'].sum().reset_index()
        
        # Create line chart
        fig_line = go.Figure()
        
        colors = {
            'CAPEX': '#a65d57',  # error color
            'OPEX': '#5a7a8c',   # info color
            'COGS': '#4a7c59'    # success color
        }
        
        for expense_type in ['CAPEX', 'OPEX', 'COGS']:
            type_data = monthly_by_type[monthly_by_type['type'] == expense_type]
            fig_line.add_trace(go.Scatter(
                x=type_data['month'],
                y=type_data['grand_total'],
                mode='lines+markers',
                name=expense_type,
                line=dict(color=colors.get(expense_type, '#000000'), width=2),
                marker=dict(size=6)
            ))
        
        fig_line.update_layout(
            title="Expenses Over Time by Type",
            xaxis_title="Month",
            yaxis_title="Amount (฿)",
            font=dict(family="Helvetica Neue, Helvetica, Arial, sans-serif", size=10, color="#000000"),
            plot_bgcolor='#fafaf8',
            paper_bgcolor='white',
            height=400,
            margin=dict(l=50, r=50, t=50, b=50),
            legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1)
        )
        
        # Create pie charts for each type
        pie_charts = []
        
        for expense_type in ['COGS', 'OPEX', 'CAPEX']:
            type_df = df[df['type'] == expense_type]
            if len(type_df) > 0:
                # Group by category (using subcategory_free as category)
                category_totals = type_df.groupby('subcategory_free')['grand_total'].sum().reset_index()
                category_totals = category_totals.sort_values('grand_total', ascending=False)
                
                fig_pie = go.Figure(data=[go.Pie(
                    labels=category_totals['subcategory_free'],
                    values=category_totals['grand_total'],
                    hole=0.3,
                    marker=dict(colors=px.colors.qualitative.Set3)
                )])
                
                fig_pie.update_layout(
                    title=f"{expense_type} by Category",
                    font=dict(family="Helvetica Neue, Helvetica, Arial, sans-serif", size=10, color="#000000"),
                    height=350,
                    margin=dict(l=20, r=20, t=40, b=20),
                    paper_bgcolor='white',
                )
                
                pie_charts.append(
                    dcc.Graph(figure=fig_pie, config={'displayModeBar': False})
                )
            else:
                pie_charts.append(
                    html.Div(f"No {expense_type} data", className="text-center", 
                            style={"height": "350px", "display": "flex", "alignItems": "center", "justifyContent": "center"})
                )
        
        # Create summary table
        summary_data = df.groupby('type').agg({
            'grand_total': 'sum',
            'doc_no': 'count'
        }).reset_index()
        summary_data.columns = ['Type', 'Total Amount', 'Count']
        summary_data['Total Amount'] = summary_data['Total Amount'].apply(lambda x: f"฿{x:,.2f}")
        
        # Add grand total row
        total_row = pd.DataFrame({
            'Type': ['TOTAL'],
            'Total Amount': [f"฿{df['grand_total'].sum():,.2f}"],
            'Count': [len(df)]
        })
        summary_data = pd.concat([summary_data, total_row], ignore_index=True)
        
        summary_table = dash_table.DataTable(
            data=summary_data.to_dict('records'),
            columns=[
                {"name": "Type", "id": "Type"},
                {"name": "Total Amount", "id": "Total Amount"},
                {"name": "Count", "id": "Count"},
            ],
            style_table={'overflowX': 'auto'},
            style_cell={
                'textAlign': 'left',
                'padding': '12px',
                'fontFamily': 'Helvetica Neue Light, Helvetica Neue, Helvetica, Arial, sans-serif',
                'fontSize': '10pt',
                'color': '#000000',
            },
            style_header={
                'backgroundColor': '#f5f5f2',
                'fontWeight': '500',
                'fontFamily': 'Helvetica Neue, Helvetica, Arial, sans-serif',
                'fontSize': '12pt',
                'color': '#000000',
                'borderBottom': '2px solid #d4d4cd',
            },
            style_data={
                'borderBottom': '1px solid #e8e8e3',
            },
            style_data_conditional=[
                {
                    'if': {'filter_query': '{Type} = "TOTAL"'},
                    'fontWeight': '700',
                    'backgroundColor': '#f5f5f2',
                    'borderTop': '3px double #4a4a45',
                }
            ],
        )
        
        return html.Div([
            # Info text
            html.P(
                f"Expenses Report: {params.get('start_date', 'All')} to {params.get('end_date', 'All')} | "
                f"Location: {location or 'All'} | Total: {data['total']} expenses",
                className="info-text mb-3"
            ),
            
            # Row 1: Line chart
            html.Div([
                dcc.Graph(figure=fig_line, config={'displayModeBar': False})
            ], className="mb-4"),
            
            # Row 2: Pie charts
            html.Div([
                html.Div(pie_charts, 
                        style={"display": "grid", "gridTemplateColumns": "repeat(3, 1fr)", "gap": "1rem"})
            ], className="mb-4"),
            
            # Row 3: Summary table
            html.Div([
                html.H5("Summary", className="mb-3"),
                summary_table
            ])
        ])
        
    except Exception as e:
        return html.Div(f"Error loading Expenses Report: {str(e)}", style={"color": "#a65d57"})

