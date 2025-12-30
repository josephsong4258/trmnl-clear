#!/bin/bash
# Railway startup script

echo "🚀 Starting TRMNL James Clear Quotes Plugin..."

# Create data directory
mkdir -p data

# Check if quotes database exists or is too small (< 100 quotes)
if [ ! -f "data/quotes.json" ]; then
    echo "📚 No quotes database found. Running initial scrape..."
    python src/scraper.py
    echo "✅ Scraping complete!"
elif [ $(wc -l < data/quotes.json) -lt 10 ]; then
    echo "📚 Quotes database too small. Re-scraping..."
    python src/scraper.py
    echo "✅ Scraping complete!"
else
    echo "✅ Quotes database found with $(python -c "import json; print(len(json.load(open('data/quotes.json'))))" 2>/dev/null || echo "unknown") quotes"
fi

# Start the server
echo "🌐 Starting Flask server on port $PORT..."
exec gunicorn -w 4 -b 0.0.0.0:$PORT src.server:app