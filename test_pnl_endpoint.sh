#!/bin/bash

# Test script for P&L Report endpoint
# Usage: ./test_pnl_endpoint.sh

BASE_URL="http://localhost:8000/api/v1/reports"

echo "========================================="
echo "Testing P&L Report API"
echo "========================================="
echo ""

# Test 1: Yearly format - All locations
echo "1. Yearly P&L Report - All Locations"
echo "   GET ${BASE_URL}/pnl?start_date=01/11/2025&end_date=31/12/2025&format=yearly"
curl -s "${BASE_URL}/pnl?start_date=01/11/2025&end_date=31/12/2025&format=yearly" | python3 -c "
import json, sys
data = json.load(sys.stdin)
print(f\"   Period: {data['report_info']['start_date']} to {data['report_info']['end_date']}\")
print(f\"   Format: {data['report_info']['format']}\")
print(f\"   Location: {data['report_info']['location']}\")
print(f\"   Periods: {data['report_info']['periods']}\")
print(f\"   \")
print(f\"   Revenue by Customer:\")
for customer, amounts in data['revenue']['revenue_by_customer'].items():
    print(f\"     - {customer}: {amounts['Total']:.2f}\")
print(f\"   Total Revenue: {data['revenue']['total_net_revenue']['Total']:.2f}\")
print(f\"   Total COGS: {data['cogs']['total']['Total']:.2f}\")
print(f\"   Gross Profit: {data['gross_profit']['Total']:.2f}\")
print(f\"   Total OPEX: {data['operating_expenses']['total']['Total']:.2f}\")
print(f\"   EBIT: {data['ebit']['Total']:.2f}\")
print(f\"   Income Tax: {data['income_tax']['Total']:.2f}\")
print(f\"   Net Earnings: {data['net_earnings']['Total']:.2f}\")
"
echo ""
echo ""

# Test 2: Monthly format - All locations
echo "2. Monthly P&L Report - All Locations"
echo "   GET ${BASE_URL}/pnl?start_date=01/11/2025&end_date=31/12/2025&format=monthly"
curl -s "${BASE_URL}/pnl?start_date=01/11/2025&end_date=31/12/2025&format=monthly" | python3 -c "
import json, sys
data = json.load(sys.stdin)
print(f\"   Periods: {data['report_info']['periods']}\")
print(f\"   \")
print(f\"   Revenue by Customer:\")
for customer, amounts in data['revenue']['revenue_by_customer'].items():
    print(f\"     - {customer}:\")
    for period, amount in amounts.items():
        print(f\"       {period}: {amount:.2f}\")
print(f\"   \")
print(f\"   Total Revenue per period:\")
for period, amount in data['revenue']['total_net_revenue'].items():
    print(f\"     {period}: {amount:.2f}\")
print(f\"   \")
print(f\"   EBIT per period:\")
for period, amount in data['ebit'].items():
    print(f\"     {period}: {amount:.2f}\")
print(f\"   \")
print(f\"   Net Earnings per period:\")
for period, amount in data['net_earnings'].items():
    print(f\"     {period}: {amount:.2f}\")
"
echo ""
echo ""

# Test 3: Yearly format - Specific location (Bkk)
echo "3. Yearly P&L Report - Bkk Location Only"
echo "   GET ${BASE_URL}/pnl?start_date=01/11/2025&end_date=31/12/2025&format=yearly&location=Bkk"
curl -s "${BASE_URL}/pnl?start_date=01/11/2025&end_date=31/12/2025&format=yearly&location=Bkk" | python3 -c "
import json, sys
data = json.load(sys.stdin)
print(f\"   Location Filter: {data['report_info']['location']}\")
print(f\"   Total Revenue: {data['revenue']['total_net_revenue']['Total']:.2f}\")
print(f\"   Total COGS: {data['cogs']['total']['Total']:.2f}\")
print(f\"   Total OPEX: {data['operating_expenses']['total']['Total']:.2f}\")
print(f\"   Net Earnings: {data['net_earnings']['Total']:.2f}\")
"
echo ""
echo ""

# Test 4: COGS breakdown
echo "4. COGS Breakdown (Category → Subcategory)"
echo "   GET ${BASE_URL}/pnl?start_date=01/11/2025&end_date=31/12/2025&format=yearly"
curl -s "${BASE_URL}/pnl?start_date=01/11/2025&end_date=31/12/2025&format=yearly" | python3 -c "
import json, sys
data = json.load(sys.stdin)
print(f\"   COGS Categories:\")
for category, cat_data in data['cogs']['expenses_by_category'].items():
    print(f\"     {category}:\")
    for subcat, amounts in cat_data.get('subcategories', {}).items():
        print(f\"       - {subcat}: {amounts['Total']:.2f}\")
    if 'direct' in cat_data:
        print(f\"       - (Direct): {cat_data['direct']['Total']:.2f}\")
print(f\"   Total COGS: {data['cogs']['total']['Total']:.2f}\")
"
echo ""
echo ""

# Test 5: OPEX breakdown (first 5 categories)
echo "5. OPEX Breakdown - First 5 Categories"
echo "   GET ${BASE_URL}/pnl?start_date=01/11/2025&end_date=31/12/2025&format=yearly"
curl -s "${BASE_URL}/pnl?start_date=01/11/2025&end_date=31/12/2025&format=yearly" | python3 -c "
import json, sys
data = json.load(sys.stdin)
print(f\"   OPEX Categories (showing first 5):\")
count = 0
for category, cat_data in data['operating_expenses']['expenses_by_category'].items():
    if count >= 5:
        break
    print(f\"     {category}:\")
    for subcat, amounts in cat_data.get('subcategories', {}).items():
        print(f\"       - {subcat}: {amounts['Total']:.2f}\")
    if 'direct' in cat_data:
        print(f\"       - (Direct): {cat_data['direct']['Total']:.2f}\")
    count += 1
print(f\"   Total OPEX: {data['operating_expenses']['total']['Total']:.2f}\")
"
echo ""
echo ""

# Test 6: Test date range validation (should fail - more than 12 months)
echo "6. Test Date Range Validation (>12 months - should fail)"
echo "   GET ${BASE_URL}/pnl?start_date=01/01/2024&end_date=31/03/2025&format=yearly"
response=$(curl -s "${BASE_URL}/pnl?start_date=01/01/2024&end_date=31/03/2025&format=yearly")
echo "$response" | python3 -c "
import json, sys
try:
    data = json.load(sys.stdin)
    if 'error' in data:
        print(f\"   ✓ Validation Error (as expected)\")
        print(f\"   Error: {data.get('detail', 'N/A')}\")
    else:
        print(f\"   ✗ Should have failed validation\")
except:
    print(f\"   ✗ Invalid response\")
"
echo ""
echo ""

# Test 7: Test invalid format (should fail)
echo "7. Test Invalid Format (should fail)"
echo "   GET ${BASE_URL}/pnl?start_date=01/11/2025&end_date=31/12/2025&format=weekly"
response=$(curl -s "${BASE_URL}/pnl?start_date=01/11/2025&end_date=31/12/2025&format=weekly")
echo "$response" | python3 -c "
import json, sys
try:
    data = json.load(sys.stdin)
    if 'error' in data or 'detail' in data:
        print(f\"   ✓ Validation Error (as expected)\")
        print(f\"   Error: {data.get('detail', 'N/A')}\")
    else:
        print(f\"   ✗ Should have failed validation\")
except:
    print(f\"   ✗ Invalid response\")
"
echo ""
echo ""

echo "========================================="
echo "All P&L Report tests completed!"
echo "========================================="
echo ""
echo "For interactive testing, visit:"
echo "  http://localhost:8000/docs"
echo ""
echo "For detailed documentation, see:"
echo "  - README.md"

