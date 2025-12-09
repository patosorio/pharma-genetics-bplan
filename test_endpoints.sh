#!/bin/bash

# Quick test script for Income and Expenses API endpoints
# Usage: ./test_endpoints.sh

BASE_URL="http://localhost:8000/api/v1"

echo "========================================="
echo "Testing Hi Tai Business Plan API"
echo "========================================="
echo ""

# Test 1: Health Check
echo "1. Health Check"
echo "   GET /health"
curl -s http://localhost:8000/health | python3 -m json.tool | head -10
echo ""
echo ""

# Test 2: List all income
echo "2. List All Income"
echo "   GET ${BASE_URL}/income"
curl -s "${BASE_URL}/income" | python3 -c "import json, sys; data = json.load(sys.stdin); print(f\"   Total records: {data['total']}\"); print(f\"   Filters: {data['filters_applied']}\")"
echo ""
echo ""

# Test 3: List all expenses
echo "3. List All Expenses"
echo "   GET ${BASE_URL}/expenses"
curl -s "${BASE_URL}/expenses" | python3 -c "import json, sys; data = json.load(sys.stdin); print(f\"   Total records: {data['total']}\"); print(f\"   Filters: {data['filters_applied']}\")"
echo ""
echo ""

# Test 4: Filter income by date range (DD/MM/YYYY format)
echo "4. Filter Income by Date Range (DD/MM/YYYY)"
echo "   GET ${BASE_URL}/income?start_date=01/12/2025&end_date=31/12/2025"
curl -s "${BASE_URL}/income?start_date=01/12/2025&end_date=31/12/2025" | python3 -c "import json, sys; data = json.load(sys.stdin); print(f\"   Total records: {data['total']}\"); print(f\"   Filters: {data['filters_applied']}\")"
echo ""
echo ""

# Test 5: Filter expenses by location
echo "5. Filter Expenses by Location"
echo "   GET ${BASE_URL}/expenses?location=Pattaya"
curl -s "${BASE_URL}/expenses?location=Pattaya" | python3 -c "import json, sys; data = json.load(sys.stdin); print(f\"   Total records: {data['total']}\"); print(f\"   Filters: {data['filters_applied']}\")"
echo ""
echo ""

# Test 6: Combine filters (DD/MM/YYYY format)
echo "6. Combine Multiple Filters"
echo "   GET ${BASE_URL}/income?start_date=01/11/2025&end_date=31/12/2025&location=Bkk"
curl -s "${BASE_URL}/income?start_date=01/11/2025&end_date=31/12/2025&location=Bkk" | python3 -c "import json, sys; data = json.load(sys.stdin); print(f\"   Total records: {data['total']}\"); print(f\"   Filters: {data['filters_applied']}\")"
echo ""
echo ""

# Test 7: Invalid date format (should return 422)
echo "7. Test Invalid Date Format (Validation - wrong format YYYY-MM-DD)"
echo "   GET ${BASE_URL}/income?start_date=2025-12-01"
response=$(curl -s "${BASE_URL}/income?start_date=2025-12-01")
echo "$response" | python3 -c "import json, sys; data = json.load(sys.stdin); print(f\"   Error: {data.get('error', False)}\"); print(f\"   Status: {data.get('status_code', 'N/A')}\"); print(f\"   Detail: {data.get('detail', 'N/A')}\")"
echo ""
echo ""

# Test 8: Empty results (DD/MM/YYYY format)
echo "8. Test Empty Results"
echo "   GET ${BASE_URL}/income?start_date=01/01/2026"
curl -s "${BASE_URL}/income?start_date=01/01/2026" | python3 -c "import json, sys; data = json.load(sys.stdin); print(f\"   Total records: {data['total']}\"); print(f\"   Filters: {data['filters_applied']}\")"
echo ""
echo ""

echo "========================================="
echo "All tests completed!"
echo "========================================="
echo ""
echo "For interactive testing, visit:"
echo "  http://localhost:8000/docs"
echo ""
echo "For detailed documentation, see:"
echo "  - README.md"

