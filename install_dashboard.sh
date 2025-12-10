#!/bin/bash

# Hi Tai Dashboard Installation Script

echo "======================================"
echo "Hi Tai Dashboard Setup"
echo "======================================"
echo ""

# Check if virtual environment is activated
if [ -z "$VIRTUAL_ENV" ]; then
    echo "⚠️  Warning: Virtual environment not detected"
    echo "   It's recommended to activate your virtual environment first:"
    echo "   source env/bin/activate"
    echo ""
    read -p "Continue anyway? (y/n) " -n 1 -r
    echo ""
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        exit 1
    fi
fi

echo "📦 Installing dashboard dependencies..."
pip install dash-bootstrap-components==1.6.0

if [ $? -eq 0 ]; then
    echo "✅ Dependencies installed successfully!"
else
    echo "❌ Failed to install dependencies"
    exit 1
fi

echo ""
echo "======================================"
echo "✅ Dashboard setup complete!"
echo "======================================"
echo ""
echo "To start the application:"
echo "  uvicorn src.main:app --host 0.0.0.0 --port 8000 --reload"
echo ""
echo "Once running, access:"
echo "  📊 Dashboard: http://localhost:8000/dashboard/"
echo "  📖 API Docs:  http://localhost:8000/docs"
echo ""

