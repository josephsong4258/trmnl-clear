#!/bin/bash
# Railway startup script

echo "🚀 Starting TRMNL James Clear Quotes Plugin..."

# Create data directory
mkdir -p data

# Check if quotes database exists
if [ ! -f "data/quotes.json" ]; then
    echo "📚 No quotes database found. Running initial scrape..."
    python src/scraper.py || echo "⚠️  Scraper failed, will use sample quotes"
else
    echo "✅ Quotes database found ($(wc -l < data/quotes.json) lines)"
fi

# Start the server
echo "🌐 Starting Flask server..."
exec gunicorn -w 4 -b 0.0.0.0:$PORT src.server:app
