# Hi Tai Dashboard

## Quick Start

```bash
# Install dependencies (if not already installed)
pip install dash-bootstrap-components==1.6.0

# Or use the installation script
./install_dashboard.sh

# Start the server
uvicorn src.main:app --host 0.0.0.0 --port 8000 --reload

# Access the dashboard
# http://localhost:8000/dashboard/
```

## Architecture

```
┌─────────────────────────────────────────────────────────┐
│                     FastAPI App                          │
│                   (src/main.py)                          │
│                                                           │
│  ┌─────────────────────────────────────────────────┐   │
│  │            Dash App                              │   │
│  │        (dashboard/app.py)                        │   │
│  │                                                   │   │
│  │  Server: fastapi_app                            │   │
│  │  URL: /dashboard/                               │   │
│  │                                                   │   │
│  │  ┌───────────────────────────────────────┐     │   │
│  │  │         Layout                         │     │   │
│  │  │    (dashboard/layout.py)               │     │   │
│  │  │                                         │     │   │
│  │  │  • Sidebar Navigation                  │     │   │
│  │  │  • Filter Controls                     │     │   │
│  │  │  • Tab Content                         │     │   │
│  │  │  • Custom CSS                          │     │   │
│  │  └───────────────────────────────────────┘     │   │
│  │                                                   │   │
│  │  ┌───────────────────────────────────────┐     │   │
│  │  │        Callbacks                       │     │   │
│  │  │    (dashboard/callbacks.py)            │     │   │
│  │  │                                         │     │   │
│  │  │  • Navigation Logic                    │     │   │
│  │  │  • API Calls                           │     │   │
│  │  │  • Data Display                        │     │   │
│  │  └───────────────────────────────────────┘     │   │
│  └─────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────┘
```

## Features

### 1. Expenses Tab
- View all expense records
- Filter by location, date range
- Display: Doc No, Date, Supplier, Type, Location, Amount, VAT, Total, Status
- Sortable, paginated table

### 2. Income Tab
- View all income records
- Filter by location, date range
- Display: Doc No, Date, Customer, Location, Amount, VAT, Total, Status
- Sortable, paginated table

### 3. P&L Tab
- Comprehensive Profit & Loss statement
- Filter by location, date range, format (yearly/monthly)
- Sections:
  - Revenue (by customer)
  - COGS (by category/subcategory)
  - Gross Profit
  - Operating Expenses (by category/subcategory)
  - EBIT
  - Income Tax (15%)
  - Net Earnings

### 4. Cashflow Tab
- Complete cashflow analysis
- Filter by location, date range, format (yearly/monthly)
- Opening balance input
- Sections:
  - Cash Inflows (Sales, Fundings, Other)
  - Cash Outflows (COGS, OPEX, CAPEX)
  - Net Cashflow
  - Opening/Closing Balance

## Design System

### Colors
```css
/* Primary - Military/Olive Greens */
--primary-900: #2d3b23;
--primary-800: #3d4f2f;
--primary-700: #4a5d3a;
--primary-600: #556b2f;
--primary-500: #6b7f4a;

/* Neutrals - Warm grays */
--neutral-50: #fafaf8;
--neutral-100: #f5f5f2;
--neutral-200: #e8e8e3;
--neutral-300: #d4d4cd;
--neutral-700: #4a4a45;
--neutral-900: #1a1a18;

/* Accents */
--gold: #b8a361;
--gold-muted: #c9bc8e;

/* Status Colors */
--success: #4a7c59;
--warning: #c4a035;
--error: #a65d57;
--info: #5a7a8c;
```

### Typography
- **Titles & Headers**: Helvetica Neue, 12pt (500 weight)
- **Body Text**: Helvetica Neue Light, 10pt
- **Color**: Black (#000000)

### Layout
- **Sidebar**: 250px wide, collapsible
- **Content Area**: Responsive, adjusts with sidebar
- **Tables**: Clean, minimal borders
- **Cards**: White background with subtle borders

## API Integration

The dashboard consumes these existing API endpoints:

| Endpoint | Method | Purpose |
|----------|--------|---------|
| `/api/v1/expenses` | GET | List expenses with filters |
| `/api/v1/income` | GET | List income with filters |
| `/api/v1/reports/pnl` | GET | Generate P&L report |
| `/api/v1/reports/cashflow` | GET | Generate Cashflow report |

All endpoints support:
- Date range filtering (DD/MM/YYYY format)
- Location filtering
- Format selection (yearly/monthly) for reports

## File Structure

```
dashboard/
├── __init__.py          # Auto-imports dash_app
├── app.py               # Dash app initialization
├── layout.py            # UI components and styling
└── callbacks.py         # Interactive logic

Changes to existing files:
src/main.py              # Added: import dashboard (line 124)
requirements.txt         # Added: dash-bootstrap-components==1.6.0
```

## Development

### Adding a New Tab

1. **Create layout function** in `layout.py`:
```python
def create_my_new_tab():
    return html.Div([
        html.H3("My New Tab"),
        # Add your content here
    ])
```

2. **Add navigation link** in `create_sidebar()`:
```python
dbc.NavLink("My Tab", href="#", id="nav-mytab", className="nav-link"),
```

3. **Add callback** in `callbacks.py`:
```python
@dash_app.callback(
    Output("mytab-content", "children"),
    [Input("apply-filters", "n_clicks"),
     Input("active-tab", "data")],
    [State("location-filter", "value")]
)
def update_mytab(n_clicks, active_tab, location):
    if active_tab != "mytab":
        raise PreventUpdate
    # Your logic here
```

4. **Update navigation callback** to include the new tab

### Customizing Styles

All styles are in `layout.py` in the `CUSTOM_CSS` string. Modify CSS variables or add new styles as needed.

### Debugging

- Check browser console for JavaScript errors
- Check terminal for Python errors
- Verify API endpoints work at http://localhost:8000/docs
- Use `print()` statements in callbacks for debugging

## Notes

- No changes made to existing src/ files (except 1 line in main.py)
- All models, services, and API routes remain unchanged
- Dashboard runs on same port as FastAPI
- Uses existing authentication (if any)
- Fully responsive design
- Production-ready with error handling

