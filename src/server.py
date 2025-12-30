"""
TRMNL Plugin Server
Flask server that responds to TRMNL's plugin requests
"""

from flask import Flask, request, jsonify, send_file
import json
import os
from datetime import datetime
import sys

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from display_manager import QuoteDisplayManager

app = Flask(__name__)

# Get refresh interval from environment variable (default: daily)
# Options: 'daily', 'hourly', 'every_request'
REFRESH_INTERVAL = os.environ.get('QUOTE_REFRESH_INTERVAL', 'daily')

# Initialize quote manager - create sample quotes if database doesn't exist
try:
    quote_manager = QuoteDisplayManager('data/quotes.json', refresh_interval=REFRESH_INTERVAL)
    if not quote_manager.quotes:
        raise FileNotFoundError("No quotes loaded")
except (FileNotFoundError, json.JSONDecodeError):
    # Create sample quotes for initial deployment
    print("⚠️  No quotes database found. Creating sample quotes...")
    os.makedirs('data', exist_ok=True)

    sample_quotes = [
        {
            'text': 'Every action you take is a vote for the type of person you wish to become.',
            'category': 'atomic-habits',
            'source': 'James Clear',
            'length': 76,
            'scraped_at': datetime.now().isoformat()
        },
        {
            'text': 'You do not rise to the level of your goals. You fall to the level of your systems.',
            'category': 'atomic-habits',
            'source': 'James Clear',
            'length': 84,
            'scraped_at': datetime.now().isoformat()
        },
        {
            'text': 'Habits are the compound interest of self-improvement.',
            'category': 'atomic-habits',
            'source': 'James Clear',
            'length': 54,
            'scraped_at': datetime.now().isoformat()
        }
    ]

    with open('data/quotes.json', 'w') as f:
        json.dump(sample_quotes, f, indent=2)

    quote_manager = QuoteDisplayManager('data/quotes.json', refresh_interval=REFRESH_INTERVAL)
    print(f"✅ Created sample database with {len(sample_quotes)} quotes")
    print(f"   Quote refresh interval: {REFRESH_INTERVAL}")
    print("   Trigger full scrape: POST to /trigger-scrape endpoint")


def generate_markup_full(quote_data: dict) -> str:
    """Generate HTML markup for full screen layout with dynamic font sizing"""

    # Adjust font size based on quote length
    text_length = len(quote_data['text'])

    if text_length < 150:
        font_size = '1.4em'
        line_height = '1.8'
    elif text_length < 300:
        font_size = '1.2em'
        line_height = '1.6'
    elif text_length < 600:
        font_size = '1.0em'
        line_height = '1.5'
    else:
        # Very long quotes
        font_size = '0.85em'
        line_height = '1.4'

    return f"""
    <div class="view view--full">
        <div class="layout">
            <div class="columns">
                <div class="column">
                    <div class="markdown gap--large">
                        <span class="title">Daily Wisdom</span>
                        <div class="content-element content content--center" style="font-size: {font_size}; line-height: {line_height};">
                            "{quote_data['text']}"
                        </div>
                    </div>
                </div>
            </div>
        </div>
    </div>
    """


def generate_markup_half_vertical(quote_data: dict) -> str:
    """Generate HTML markup for half vertical layout"""
    return f"""
    <div class="view view--half_vertical">
        <div class="layout">
            <div class="markdown gap--medium">
                <span class="subtitle">Daily Wisdom</span>
                <div class="content-element content" style="font-size: 0.95em;">
                    "{quote_data['text']}"
                </div>
            </div>
        </div>
    </div>
    """


def generate_markup_half_horizontal(quote_data: dict) -> str:
    """Generate HTML markup for half horizontal layout"""
    return f"""
    <div class="view view--half_horizontal">
        <div class="layout">
            <div class="markdown gap--medium">
                <span class="subtitle">Daily Wisdom</span>
                <div class="content-element content" style="font-size: 0.9em;">
                    "{quote_data['text']}"
                </div>
            </div>
        </div>
    </div>
    """


def generate_markup_quadrant(quote_data: dict) -> str:
    """Generate HTML markup for quadrant layout"""
    return f"""
    <div class="view view--quadrant">
        <div class="markdown gap--small">
            <span class="label">Wisdom</span>
            <div class="content-element" style="font-size: 0.8em;">
                "{quote_data['text']}"
            </div>
        </div>
    </div>
    """


@app.route('/plugin', methods=['GET', 'POST'])
def plugin_endpoint():
    """
    Main plugin endpoint that TRMNL calls to generate screen content

    Request includes:
    - user_uuid: Unique user identifier
    - trmnl: Metadata object with device info
    - refresh_interval: User's selected refresh interval (from form fields)

    Headers include:
    - Authorization: Bearer token for the user's plugin connection
    """
    try:
        # Get request data (works for both GET and POST)
        if request.method == 'POST':
            user_uuid = request.form.get('user_uuid')
            trmnl_data = request.form.get('trmnl')
            user_refresh_interval = request.form.get('refresh_interval', REFRESH_INTERVAL)
        else:
            user_uuid = request.args.get('user_uuid')
            trmnl_data = request.args.get('trmnl')
            user_refresh_interval = request.args.get('refresh_interval', REFRESH_INTERVAL)

        # Parse TRMNL metadata if present
        metadata = json.loads(trmnl_data) if trmnl_data else {}

        # Get device dimensions for layout optimization
        device = metadata.get('device', {})
        width = device.get('width', 800)
        height = device.get('height', 480)

        # Create a temporary quote manager with user's refresh interval preference
        temp_manager = QuoteDisplayManager('data/quotes.json', refresh_interval=user_refresh_interval)

        # Get quotes for each layout type
        quote_full = temp_manager.get_daily_quote('full')
        quote_half_v = temp_manager.get_daily_quote('half_vertical')
        quote_half_h = temp_manager.get_daily_quote('half_horizontal')
        quote_quad = temp_manager.get_daily_quote('quadrant')

        # Generate markup for all layouts
        response = {
            'markup': generate_markup_full(quote_full) if quote_full else '',
            'markup_half_vertical': generate_markup_half_vertical(quote_half_v) if quote_half_v else '',
            'markup_half_horizontal': generate_markup_half_horizontal(quote_half_h) if quote_half_h else '',
            'markup_quadrant': generate_markup_quadrant(quote_quad) if quote_quad else '',
            'shared': '',  # Optional: shared data between layouts
        }

        return jsonify(response)

    except Exception as e:
        print(f"Error generating plugin content: {e}")
        return jsonify({'error': str(e)}), 500


@app.route('/webhook/newsletter', methods=['POST'])
def newsletter_webhook():
    """
    Webhook endpoint for receiving new newsletter quotes
    Can be triggered by Zapier, Make, or other automation services
    """
    try:
        data = request.get_json()

        # Extract quotes from webhook data
        quotes = data.get('quotes', [])

        # Add to quotes database
        quotes_file = 'data/quotes.json'
        existing_quotes = []

        # Ensure data directory exists
        os.makedirs('data', exist_ok=True)

        if os.path.exists(quotes_file):
            with open(quotes_file, 'r', encoding='utf-8') as f:
                existing_quotes = json.load(f)

        # Add new quotes
        for quote_text in quotes:
            new_quote = {
                'text': quote_text,
                'category': '3-2-1-newsletter',
                'source': 'James Clear - 3-2-1 Newsletter',
                'length': len(quote_text),
                'scraped_at': datetime.now().isoformat()
            }
            existing_quotes.append(new_quote)

        # Save updated quotes
        with open(quotes_file, 'w', encoding='utf-8') as f:
            json.dump(existing_quotes, f, indent=2, ensure_ascii=False)

        # Reload quote manager
        global quote_manager
        quote_manager = QuoteDisplayManager('data/quotes.json')

        return jsonify({'status': 'success', 'added': len(quotes)})

    except Exception as e:
        print(f"Error processing newsletter webhook: {e}")
        return jsonify({'error': str(e)}), 500


@app.route('/stats', methods=['GET'])
def get_stats():
    """Get statistics about the quote database"""
    stats = quote_manager.get_stats()
    return jsonify(stats)


@app.route('/download-quotes', methods=['GET'])
def download_quotes():
    """Download the quotes.json file"""
    try:
        return send_file('data/quotes.json',
                        mimetype='application/json',
                        as_attachment=True,
                        download_name='quotes.json')
    except Exception as e:
        return jsonify({'error': str(e)}), 404


@app.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({
        'status': 'healthy',
        'timestamp': datetime.now().isoformat(),
        'quotes_loaded': len(quote_manager.quotes)
    })


@app.route('/trigger-scrape', methods=['POST'])
def trigger_scrape():
    """
    Trigger the quote scraper manually
    Scrapes both website categories AND newsletter
    """
    try:
        print("🔄 Scraper triggered via API...")

        # Import scrapers
        sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
        from scraper import JamesClearScraper
        from newsletter_scraper import NewsletterWebScraper

        # 1. Scrape website categories
        print("📚 Scraping website categories...")
        scraper = JamesClearScraper()
        quotes = scraper.scrape_all_categories()

        if quotes:
            scraper.save_quotes(quotes, 'data/quotes.json')
            print(f"✅ Saved {len(quotes)} website quotes")

        # 2. Scrape newsletter
        print("📧 Scraping newsletter...")
        newsletter_scraper = NewsletterWebScraper()
        latest_newsletter = newsletter_scraper.get_latest_ideas()

        newsletter_count = 0
        if latest_newsletter and latest_newsletter.get('ideas'):
            # Load existing quotes
            with open('data/quotes.json', 'r', encoding='utf-8') as f:
                existing_quotes = json.load(f)

            # Add newsletter ideas
            for idea_text in latest_newsletter['ideas']:
                # Check if already exists
                if not any(q['text'] == idea_text for q in existing_quotes):
                    new_quote = {
                        'text': idea_text,
                        'category': '3-2-1-newsletter',
                        'source': 'James Clear - 3-2-1 Newsletter',
                        'length': len(idea_text),
                        'scraped_at': datetime.now().isoformat()
                    }
                    existing_quotes.append(new_quote)
                    newsletter_count += 1

            # Save updated quotes
            with open('data/quotes.json', 'w', encoding='utf-8') as f:
                json.dump(existing_quotes, f, indent=2, ensure_ascii=False)

            print(f"✅ Added {newsletter_count} new newsletter quotes")
        else:
            print("⚠️  No newsletter quotes found")

        # Reload quote manager
        global quote_manager
        quote_manager = QuoteDisplayManager('data/quotes.json', refresh_interval=REFRESH_INTERVAL)

        return jsonify({
            'status': 'success',
            'message': f'Scraped {len(quotes)} website quotes + {newsletter_count} newsletter quotes',
            'website_quotes': len(quotes),
            'newsletter_quotes': newsletter_count,
            'total_quotes': len(quote_manager.quotes)
        })

    except Exception as e:
        print(f"Error during scraping: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({
            'status': 'error',
            'message': str(e)
        }), 500


if __name__ == '__main__':
    # For development
    app.run(host='0.0.0.0', port=5000, debug=True)