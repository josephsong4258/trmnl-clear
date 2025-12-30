"""
Automated Quote Updater
Runs periodically to update the quote database
"""

import schedule
import time
import json
import os
import sys
from datetime import datetime

# Add current directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from scraper import JamesClearScraper
from newsletter_scraper import NewsletterWebScraper


class QuoteUpdater:
    """Manages periodic updates to the quote database"""

    def __init__(self, config_file: str = 'config/config.json'):
        self.config = self.load_config(config_file)
        self.scraper = JamesClearScraper()

    def load_config(self, filename: str) -> dict:
        """Load configuration"""
        if os.path.exists(filename):
            with open(filename, 'r') as f:
                return json.load(f)
        return {}

    def update_from_website(self):
        """Scrape quotes from website"""
        print(f"\n{datetime.now()} - Starting website scrape...")

        quotes = self.scraper.scrape_all_categories()

        if quotes:
            self.scraper.save_quotes(quotes, 'data/quotes.json')
            print(f"Updated {len(quotes)} quotes from website")
        else:
            print("No quotes found during scrape")

    def update_from_newsletter(self):
        """Check for new newsletter quotes using web scraper"""
        print(f"\n{datetime.now()} - Checking for newsletter updates...")

        try:
            scraper = NewsletterWebScraper()

            # Get the latest newsletter
            latest = scraper.get_latest_ideas()

            if latest and latest.get('ideas'):
                # Add to database
                self.merge_newsletter_quotes([latest])
                print(f"Found latest newsletter with {len(latest['ideas'])} ideas")
            else:
                print("No new newsletter found or couldn't extract ideas")

        except Exception as e:
            print(f"Error checking newsletters: {e}")

    def merge_newsletter_quotes(self, newsletters: list):
        """Merge newsletter quotes with existing database"""
        # Load existing quotes
        quotes_file = '../data/quotes.json'
        existing_quotes = []

        # Ensure data directory exists
        os.makedirs('../data', exist_ok=True)

        if os.path.exists(quotes_file):
            with open(quotes_file, 'r', encoding='utf-8') as f:
                existing_quotes = json.load(f)

        # Add newsletter ideas
        for newsletter in newsletters:
            # Handle both old format (quotes) and new format (ideas)
            ideas_list = newsletter.get('ideas', newsletter.get('quotes', []))
            newsletter_date = newsletter.get('date', newsletter.get('title', 'Unknown'))

            for idea_text in ideas_list:
                # Check if quote already exists
                if not any(q['text'] == idea_text for q in existing_quotes):
                    new_quote = {
                        'text': idea_text,
                        'category': '3-2-1-newsletter',
                        'source': f"3-2-1 Newsletter - {newsletter_date}",
                        'length': len(idea_text),
                        'scraped_at': datetime.now().isoformat()
                    }
                    existing_quotes.append(new_quote)

        # Save updated quotes
        with open(quotes_file, 'w', encoding='utf-8') as f:
            json.dump(existing_quotes, f, indent=2, ensure_ascii=False)

    def run_scheduled_updates(self):
        """Set up and run scheduled updates"""

        # Update from website weekly (Sundays at 2 AM)
        schedule.every().sunday.at("02:00").do(self.update_from_website)

        # Check for newsletter updates daily (Tuesdays at 3 PM for 3-2-1 Thursday)
        schedule.every().tuesday.at("15:00").do(self.update_from_newsletter)

        # Also check Wednesday morning in case newsletter was delayed
        schedule.every().wednesday.at("09:00").do(self.update_from_newsletter)

        print("Quote updater scheduled:")
        print("- Website scrape: Every Sunday at 2:00 AM")
        print("- Newsletter check: Every Tuesday at 3:00 PM and Wednesday at 9:00 AM")
        print("\nRunning indefinitely... (Ctrl+C to stop)")

        # Initial update
        print("\nRunning initial update...")
        self.update_from_website()

        # Keep running
        while True:
            schedule.run_pending()
            time.sleep(60)  # Check every minute


if __name__ == '__main__':
    updater = QuoteUpdater()
    updater.run_scheduled_updates()