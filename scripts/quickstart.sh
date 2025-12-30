#!/bin/bash

# Quick Start Script for Atomic TRMNL Plugin

echo "Atomic TRMNL Plugin - Quick Start"
echo "=========================================="
echo ""

# Check Python
if ! command -v python3 &> /dev/null; then
    echo "Python 3 is not installed. Please install Python 3.8 or higher."
    exit 1
fi

echo "Python found: $(python3 --version)"

# Install dependencies
echo ""
echo "Installing dependencies..."
pip3 install -r requirements.txt

if [ $? -ne 0 ]; then
    echo "Failed to install dependencies"
    exit 1
fi

echo "Dependencies installed"

# Run initial scrape
echo ""
echo "Running initial quote scrape (this may take a minute)..."
python3 scraper.py

if [ ! -f "quotes.json" ]; then
    echo "Failed to create quotes.json"
    exit 1
fi

QUOTE_COUNT=$(python3 -c "import json; print(len(json.load(open('quotes.json'))))")
echo "Scraped $QUOTE_COUNT quotes"

# Create config from template
if [ ! -f "config.json" ]; then
    echo ""
    echo "Creating config.json from template..."
    cp config.json.template config.json
    echo "Created config.json (update with your settings if needed)"
fi

# Test the server
echo ""
echo "Testing server..."
python3 -c "from display_manager import QuoteDisplayManager; m = QuoteDisplayManager(); print('Server components working')"

echo ""
echo "=========================================="
echo "Setup complete!"
echo ""
echo "Next steps:"
echo ""
echo "1. Start the server:"
echo "   python3 server.py"
echo ""
echo "2. In another terminal, test it:"
echo "   curl -X POST http://localhost:5000/plugin -d 'user_uuid=test'"
echo ""
echo "3. Deploy to a server (see DEPLOYMENT.md)"
echo ""
echo "4. Register your plugin URL with TRMNL at:"
echo "   https://usetrmnl.com"
echo ""
echo "Optional - Enable newsletter monitoring:"
echo "   Edit config.json with your email credentials"
echo "   Then run: python3 updater.py"
echo ""