"""Dashboard layout components."""

import dash_bootstrap_components as dbc
from dash import html, dcc

# Custom CSS for colors and fonts
CUSTOM_CSS = """
/* Color Variables */
:root {
    --primary-900: #2d3b23;
    --primary-800: #3d4f2f;
    --primary-700: #4a5d3a;
    --primary-600: #556b2f;
    --primary-500: #6b7f4a;
    --neutral-50: #fafaf8;
    --neutral-100: #f5f5f2;
    --neutral-200: #e8e8e3;
    --neutral-300: #d4d4cd;
    --neutral-700: #4a4a45;
    --neutral-900: #1a1a18;
    --gold: #b8a361;
    --gold-muted: #c9bc8e;
    --success: #4a7c59;
    --warning: #c4a035;
    --error: #a65d57;
    --info: #5a7a8c;
}

/* Global Font Settings */
body {
    font-family: 'Helvetica Neue Light', 'Helvetica Neue', Helvetica, Arial, sans-serif;
    font-size: 10pt;
    color: #000000;
    background-color: var(--neutral-50);
}

/* Titles and Headers */
h1, h2, h3, h4, h5, h6, .title, .column-header {
    font-family: 'Helvetica Neue', Helvetica, Arial, sans-serif;
    font-size: 12pt;
    font-weight: 500;
    color: #000000;
}

/* Info text */
.info-text, .small-text {
    font-size: 10pt;
}

/* Sidebar */
#sidebar {
    position: fixed;
    top: 0;
    left: 0;
    bottom: 0;
    width: 250px;
    padding: 1rem;
    background-color: var(--neutral-100);
    border-right: 1px solid var(--neutral-300);
    transition: margin-left 0.3s;
    z-index: 1000;
}

#sidebar.collapsed {
    margin-left: -250px;
}

#content {
    margin-left: 250px;
    padding: 1rem;
    transition: margin-left 0.3s;
}

#content.expanded {
    margin-left: 0;
}

/* Toggle Button */
.toggle-btn {
    position: fixed;
    top: 1rem;
    left: 260px;
    z-index: 1001;
    transition: left 0.3s;
    background-color: var(--primary-600) !important;
    border: none !important;
    color: #000000 !important;
}

.toggle-btn.collapsed {
    left: 10px;
}

/* Navigation Items */
.nav-link {
    color: #000000 !important;
    font-size: 10pt;
    padding: 0.5rem 1rem;
    margin-bottom: 0.25rem;
    border-radius: 4px;
}

.nav-link:hover {
    background-color: var(--neutral-200);
}

.nav-link.active {
    background-color: var(--primary-600) !important;
    color: #000000 !important;
}

/* Cards */
.card {
    background-color: white;
    border: 1px solid var(--neutral-300);
    border-radius: 4px;
    margin-bottom: 1rem;
}

.card-header {
    background-color: var(--neutral-100);
    border-bottom: 1px solid var(--neutral-300);
    font-size: 12pt;
    color: #000000;
    padding: 0.75rem 1rem;
}

/* Tables */
table {
    width: 100%;
    border-collapse: collapse;
    font-size: 10pt;
}

thead th {
    font-family: 'Helvetica Neue', Helvetica, Arial, sans-serif;
    font-size: 12pt;
    font-weight: 500;
    background-color: var(--neutral-100);
    border-bottom: 2px solid var(--neutral-300);
    padding: 0.5rem;
    text-align: left;
    color: #000000;
}

tbody td {
    font-family: 'Helvetica Neue Light', 'Helvetica Neue', Helvetica, Arial, sans-serif;
    font-size: 10pt;
    padding: 0.5rem;
    border-bottom: 1px solid var(--neutral-200);
    color: #000000;
}

tbody tr:hover {
    background-color: var(--neutral-50);
}

/* Filters */
.filter-section {
    background-color: white;
    padding: 1rem;
    border-radius: 4px;
    border: 1px solid var(--neutral-300);
    margin-bottom: 1rem;
}

.filter-label {
    font-size: 10pt;
    font-weight: 500;
    margin-bottom: 0.25rem;
    color: #000000;
}

/* Buttons */
.btn-primary {
    background-color: var(--primary-600) !important;
    border-color: var(--primary-600) !important;
    color: #000000 !important;
    font-size: 10pt;
}

.btn-primary:hover {
    background-color: var(--primary-700) !important;
    border-color: var(--primary-700) !important;
}

/* Loading Spinner */
.loading-spinner {
    color: var(--primary-600);
}

/* DataTable Styling */
.dash-table-container {
    font-family: 'Helvetica Neue Light', 'Helvetica Neue', Helvetica, Arial, sans-serif;
}

.dash-spreadsheet td {
    font-size: 10pt !important;
}

.dash-spreadsheet th {
    font-family: 'Helvetica Neue', Helvetica, Arial, sans-serif !important;
    font-size: 12pt !important;
    font-weight: 500 !important;
}
"""

def create_sidebar():
    """Create collapsible sidebar navigation."""
    return html.Div(
        id="sidebar",
        children=[
            # Burger menu inside sidebar
            dbc.Button(
                "☰",
                id="toggle-sidebar",
                className="toggle-btn-inside",
                n_clicks=0,
                style={"marginBottom": "1rem", "width": "100%"}
            ),
            html.H4("Hi Tai", id="sidebar-title", className="text-center mb-4", style={"color": "#000000"}),
            html.Hr(id="sidebar-hr", style={"borderColor": "var(--neutral-300)"}),
            dbc.Nav(
                [
                    html.Div([
                        dbc.NavLink("Expenses", href="#", className="nav-link nav-link-header", style={"fontWeight": "600"}),
                        dbc.Nav([
                            dbc.NavLink("All Expenses", href="#", id="nav-expenses", active=True, className="nav-link nav-link-sub"),
                            dbc.NavLink("Report", href="#", id="nav-expenses-report", className="nav-link nav-link-sub"),
                        ], vertical=True, className="submenu"),
                    ], id="expenses-section"),
                    dbc.NavLink("Income", href="#", id="nav-income", className="nav-link"),
                    html.Div([
                        dbc.NavLink("Reports", href="#", className="nav-link nav-link-header", style={"fontWeight": "600"}),
                        dbc.Nav([
                            dbc.NavLink("P&L", href="#", id="nav-pnl", className="nav-link nav-link-sub"),
                            dbc.NavLink("Cashflow", href="#", id="nav-cashflow", className="nav-link nav-link-sub"),
                        ], vertical=True, className="submenu"),
                    ], id="reports-section"),
                ],
                vertical=True,
                pills=True,
                id="sidebar-nav",
            ),
        ],
    )

def create_filters(show_format=False):
    """Create filter section with location, dates, and optional format - all in one line."""
    
    # Build all columns in one row
    columns = [
        dbc.Col([
            html.Label("Location", className="filter-label"),
            dcc.Dropdown(
                id="location-filter",
                options=[
                    {"label": "All", "value": "All"},
                    {"label": "Bkk", "value": "Bkk"},
                    {"label": "Pattaya", "value": "Pattaya"},
                ],
                value="All",
                clearable=False,
                style={"fontSize": "10pt"}
            ),
        ], width=2),
        dbc.Col([
            html.Label("Start Date", className="filter-label"),
            dcc.DatePickerSingle(
                id="start-date-filter",
                date="2025-01-01",
                display_format="DD/MM/YYYY",
                style={"fontSize": "10pt"}
            ),
        ], width=2),
        dbc.Col([
            html.Label("End Date", className="filter-label"),
            dcc.DatePickerSingle(
                id="end-date-filter",
                date="2025-12-31",
                display_format="DD/MM/YYYY",
                style={"fontSize": "10pt"}
            ),
        ], width=2),
    ]
    
    # Add format column if needed
    if show_format:
        columns.append(
            dbc.Col([
                html.Label("Format", className="filter-label"),
                dcc.Dropdown(
                    id="format-filter",
                    options=[
                        {"label": "Yearly", "value": "yearly"},
                        {"label": "Monthly", "value": "monthly"},
                    ],
                    value="yearly",
                    clearable=False,
                    style={"fontSize": "10pt"}
                ),
            ], width=2)
        )
    
    # Add Apply button
    columns.append(
        dbc.Col([
            html.Label("\u00A0", className="filter-label"),  # Invisible label for alignment
            dbc.Button("Apply Filters", id="apply-filters", color="primary", style={"width": "100%"}),
        ], width=2)
    )
    
    return html.Div(
        dbc.Row(columns, align="end", className="g-3"),
        className="filter-section"
    )

def create_expenses_tab():
    """Create expenses tab content (table view)."""
    return html.Div([
        html.H3("All Expenses", className="mb-3"),
        create_filters(show_format=False),
        dcc.Loading(
            id="loading-expenses",
            type="default",
            className="loading-spinner",
            children=[
                html.Div(id="expenses-content")
            ]
        ),
    ])

def create_expenses_report_tab():
    """Create expenses report tab with visualizations."""
    return html.Div([
        html.H3("Expenses Report", className="mb-3"),
        create_filters(show_format=False),
        dcc.Loading(
            id="loading-expenses-report",
            type="default",
            className="loading-spinner",
            children=[
                html.Div(id="expenses-report-content")
            ]
        ),
    ])

def create_income_tab():
    """Create income tab content."""
    return html.Div([
        html.H3("Income", className="mb-3"),
        create_filters(show_format=False),
        dcc.Loading(
            id="loading-income",
            type="default",
            className="loading-spinner",
            children=[
                html.Div(id="income-content")
            ]
        ),
    ])

def create_pnl_tab():
    """Create P&L tab content."""
    return html.Div([
        html.H3("Profit & Loss", className="mb-3"),
        create_filters(show_format=True),
        dcc.Loading(
            id="loading-pnl",
            type="default",
            className="loading-spinner",
            children=[
                html.Div(id="pnl-content")
            ]
        ),
    ])

def create_cashflow_tab():
    """Create cashflow tab content with opening balance in filter row."""
    # Create custom filter for cashflow with opening balance
    columns = [
        dbc.Col([
            html.Label("Location", className="filter-label"),
            dcc.Dropdown(
                id="location-filter",
                options=[
                    {"label": "All", "value": "All"},
                    {"label": "Bkk", "value": "Bkk"},
                    {"label": "Pattaya", "value": "Pattaya"},
                ],
                value="All",
                clearable=False,
                style={"fontSize": "10pt"}
            ),
        ], width=2),
        dbc.Col([
            html.Label("Start Date", className="filter-label"),
            dcc.DatePickerSingle(
                id="start-date-filter",
                date="2025-01-01",
                display_format="DD/MM/YYYY",
                style={"fontSize": "10pt"}
            ),
        ], width=2),
        dbc.Col([
            html.Label("End Date", className="filter-label"),
            dcc.DatePickerSingle(
                id="end-date-filter",
                date="2025-12-31",
                display_format="DD/MM/YYYY",
                style={"fontSize": "10pt"}
            ),
        ], width=2),
        dbc.Col([
            html.Label("Format", className="filter-label"),
            dcc.Dropdown(
                id="format-filter",
                options=[
                    {"label": "Yearly", "value": "yearly"},
                    {"label": "Monthly", "value": "monthly"},
                ],
                value="yearly",
                clearable=False,
                style={"fontSize": "10pt"}
            ),
        ], width=2),
        dbc.Col([
            html.Label("Opening Balance", className="filter-label"),
            dcc.Input(
                id="opening-balance",
                type="number",
                value=0.0,
                step=0.01,
                style={"fontSize": "10pt", "width": "100%"}
            ),
        ], width=2),
        dbc.Col([
            html.Label("\u00A0", className="filter-label"),
            dbc.Button("Apply Filters", id="apply-filters", color="primary", style={"width": "100%"}),
        ], width=2),
    ]
    
    return html.Div([
        html.H3("Cashflow", className="mb-3"),
        html.Div(
            dbc.Row(columns, align="end", className="g-3"),
            className="filter-section"
        ),
        dcc.Loading(
            id="loading-cashflow",
            type="default",
            className="loading-spinner",
            children=[
                html.Div(id="cashflow-content")
            ]
        ),
    ])

def get_layout():
    """Get main dashboard layout."""
    return html.Div([
        # Store for active tab
        dcc.Store(id="active-tab", data="expenses"),
        
        # Sidebar (with toggle button inside)
        create_sidebar(),
        
        # Main content
        html.Div(
            id="content",
            children=[
                html.Div(id="tab-content")
            ]
        ),
    ])

