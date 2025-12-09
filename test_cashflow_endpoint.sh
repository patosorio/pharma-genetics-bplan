#!/bin/bash

# Test script for Cashflow Report endpoint
# Usage: ./test_cashflow_endpoint.sh

BASE_URL="http://localhost:8000/api/v1/reports"

echo "========================================="
echo "Testing Cashflow Report API"
echo "========================================="
echo ""

# Test 1: Yearly format - No opening balance
echo "1. Yearly Cashflow Report - All Locations"
echo "   GET ${BASE_URL}/cashflow?start_date=01/11/2025&end_date=31/12/2025&format=yearly"
curl -s "${BASE_URL}/cashflow?start_date=01/11/2025&end_date=31/12/2025&format=yearly" | python3 -c "
import json, sys
data = json.load(sys.stdin)
print(f\"   Period: {data['report_info']['start_date']} to {data['report_info']['end_date']}\")
print(f\"   Format: {data['report_info']['format']}\")
print(f\"   Location: {data['report_info']['location']}\")
print(f\"   \")
print(f\"   === CASH INFLOWS ===\")
print(f\"   Sales Income (with VAT): {data['cash_inflows']['sales_income']['Total']:.2f}\")
print(f\"   Fundings: {data['cash_inflows']['fundings']['Total']:.2f}\")
print(f\"   Other Income: {data['cash_inflows']['other_income']['Total']:.2f}\")
print(f\"   Total Inflows: {data['cash_inflows']['total_inflows']['Total']:.2f}\")
print(f\"   \")
print(f\"   === CASH OUTFLOWS ===\")
print(f\"   COGS: {data['cash_outflows']['cogs']['total']['Total']:.2f}\")
print(f\"   OPEX: {data['cash_outflows']['opex']['total']['Total']:.2f}\")
print(f\"   CAPEX: {data['cash_outflows']['capex']['total']['Total']:.2f}\")
print(f\"   Total Outflows: {data['cash_outflows']['total_outflows']['Total']:.2f}\")
print(f\"   \")
print(f\"   === CASHFLOW ===\")
print(f\"   Net Cashflow: {data['net_cashflow']['Total']:.2f}\")
print(f\"   Opening Balance: {data['opening_balance']['Total']:.2f}\")
print(f\"   Closing Balance: {data['closing_balance']['Total']:.2f}\")
"
echo ""
echo ""

# Test 2: Monthly format with opening balance
echo "2. Monthly Cashflow Report - With Opening Balance"
echo "   GET ${BASE_URL}/cashflow?start_date=01/11/2025&end_date=31/12/2025&format=monthly&opening_balance=100000"
curl -s "${BASE_URL}/cashflow?start_date=01/11/2025&end_date=31/12/2025&format=monthly&opening_balance=100000" | python3 -c "
import json, sys
data = json.load(sys.stdin)
print(f\"   Periods: {data['report_info']['periods']}\")
print(f\"   Opening Balance (Start): {100000:.2f}\")
print(f\"   \")
for period in data['report_info']['periods']:
    print(f\"   === {period.upper()} ===\")
    print(f\"   Sales Income: {data['cash_inflows']['sales_income'][period]:.2f}\")
    print(f\"   Total Inflows: {data['cash_inflows']['total_inflows'][period]:.2f}\")
    print(f\"   Total Outflows: {data['cash_outflows']['total_outflows'][period]:.2f}\")
    print(f\"   Net Cashflow: {data['net_cashflow'][period]:.2f}\")
    print(f\"   Opening Balance: {data['opening_balance'][period]:.2f}\")
    print(f\"   Closing Balance: {data['closing_balance'][period]:.2f}\")
    print()
"
echo ""

# Test 3: COGS breakdown
echo "3. COGS Breakdown (Category → Subcategory)"
echo "   GET ${BASE_URL}/cashflow?start_date=01/11/2025&end_date=31/12/2025&format=yearly"
curl -s "${BASE_URL}/cashflow?start_date=01/11/2025&end_date=31/12/2025&format=yearly" | python3 -c "
import json, sys
data = json.load(sys.stdin)
print(f\"   COGS Categories (with VAT):\")
for category, cat_data in data['cash_outflows']['cogs']['expenses_by_category'].items():
    print(f\"     {category}:\")
    for subcat, amounts in cat_data.get('subcategories', {}).items():
        print(f\"       - {subcat}: {amounts['Total']:.2f}\")
    if 'direct' in cat_data:
        print(f\"       - (Direct): {cat_data['direct']['Total']:.2f}\")
print(f\"   Total COGS: {data['cash_outflows']['cogs']['total']['Total']:.2f}\")
"
echo ""
echo ""

# Test 4: CAPEX breakdown (first 5 categories)
echo "4. CAPEX Breakdown - First 5 Categories"
echo "   GET ${BASE_URL}/cashflow?start_date=01/11/2025&end_date=31/12/2025&format=yearly"
curl -s "${BASE_URL}/cashflow?start_date=01/11/2025&end_date=31/12/2025&format=yearly" | python3 -c "
import json, sys
data = json.load(sys.stdin)
print(f\"   CAPEX Categories (showing first 5):\")
count = 0
for category, cat_data in data['cash_outflows']['capex']['expenses_by_category'].items():
    if count >= 5:
        break
    print(f\"     {category}:\")
    for subcat, amounts in cat_data.get('subcategories', {}).items():
        print(f\"       - {subcat}: {amounts['Total']:.2f}\")
    if 'direct' in cat_data:
        print(f\"       - (Direct): {cat_data['direct']['Total']:.2f}\")
    count += 1
print(f\"   Total CAPEX: {data['cash_outflows']['capex']['total']['Total']:.2f}\")
"
echo ""
echo ""

# Test 5: Location filter
echo "5. Cashflow Report - Bkk Location Only"
echo "   GET ${BASE_URL}/cashflow?start_date=01/11/2025&end_date=31/12/2025&format=yearly&location=Bkk"
curl -s "${BASE_URL}/cashflow?start_date=01/11/2025&end_date=31/12/2025&format=yearly&location=Bkk" | python3 -c "
import json, sys
data = json.load(sys.stdin)
print(f\"   Location Filter: {data['report_info']['location']}\")
print(f\"   Total Inflows: {data['cash_inflows']['total_inflows']['Total']:.2f}\")
print(f\"   Total Outflows: {data['cash_outflows']['total_outflows']['Total']:.2f}\")
print(f\"   Net Cashflow: {data['net_cashflow']['Total']:.2f}\")
print(f\"   Closing Balance: {data['closing_balance']['Total']:.2f}\")
"
echo ""
echo ""

# Test 6: Cumulative balance verification (monthly)
echo "6. Verify Cumulative Balance Calculation"
echo "   GET ${BASE_URL}/cashflow?start_date=01/11/2025&end_date=31/12/2025&format=monthly&opening_balance=50000"
curl -s "${BASE_URL}/cashflow?start_date=01/11/2025&end_date=31/12/2025&format=monthly&opening_balance=50000" | python3 -c "
import json, sys
data = json.load(sys.stdin)
periods = data['report_info']['periods']
print(f\"   Starting with opening balance: 50000.00\")
print()
prev_closing = None
for period in periods:
    opening = data['opening_balance'][period]
    net = data['net_cashflow'][period]
    closing = data['closing_balance'][period]
    
    if prev_closing is not None:
        match = '✓' if abs(opening - prev_closing) < 0.01 else '✗'
        print(f\"   {match} {period}: Opening ({opening:.2f}) = Previous Closing ({prev_closing:.2f})\")
    else:
        print(f\"   ✓ {period}: Opening Balance = {opening:.2f}\")
    
    calc_closing = opening + net
    match = '✓' if abs(closing - calc_closing) < 0.01 else '✗'
    print(f\"   {match} {period}: Closing ({closing:.2f}) = Opening + Net ({calc_closing:.2f})\")
    print()
    prev_closing = closing
"
echo ""

echo "========================================="
echo "All Cashflow Report tests completed!"
echo "========================================="
echo ""
echo "For interactive testing, visit:"
echo "  http://localhost:8000/docs"
echo ""
echo "For detailed documentation, see:"
echo "  - README.md"

