"""
James Clear Quote Scraper
Scrapes quotes from jamesclear.com quote pages
"""

import requests
from bs4 import BeautifulSoup
import json
import time
from datetime import datetime
from typing import List, Dict
import re


class JamesClearScraper:
    """Scrapes quotes from James Clear's website"""
    
    QUOTE_CATEGORIES = [
        'life',
        'atomic-habits',
        'deep',
        'inspiring',
        'motivational',
        'success'
    ]
    
    BASE_URL = 'https://jamesclear.com/quote'
    
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36'
        })
    
    def scrape_category(self, category: str) -> List[Dict]:
        """Scrape all quotes from a specific category page"""
        url = f"{self.BASE_URL}/{category}"
        print(f"Scraping {url}...")
        
        try:
            response = self.session.get(url, timeout=10)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.text, 'html.parser')
            quotes = []
            
            # Find all quote blocks - they're typically in blockquotes or specific divs
            # This is a generic approach - may need adjustment based on actual HTML structure
            quote_elements = soup.find_all(['blockquote', 'p'])
            
            for element in quote_elements:
                text = element.get_text(strip=True)
                
                # Filter out navigation, headers, and very short text
                if len(text) < 20 or len(text) > 1000:
                    continue
                
                # Skip common non-quote patterns
                if any(skip in text.lower() for skip in [
                    'read more', 'click here', 'subscribe', 'newsletter',
                    'james clear', 'atomic habits', 'buy now', 'get the'
                ]):
                    continue
                
                # Clean up the quote
                text = text.strip('"').strip()
                
                # Try to find source/date if available
                source_elem = element.find_next(['cite', 'span', 'small'])
                source = source_elem.get_text(strip=True) if source_elem else None
                
                quotes.append({
                    'text': text,
                    'category': category,
                    'source': source,
                    'length': len(text),
                    'scraped_at': datetime.now().isoformat()
                })
            
            print(f"Found {len(quotes)} quotes in {category}")
            return quotes
            
        except Exception as e:
            print(f"Error scraping {category}: {e}")
            return []
    
    def scrape_all_categories(self) -> List[Dict]:
        """Scrape quotes from all categories"""
        all_quotes = []
        
        for category in self.QUOTE_CATEGORIES:
            quotes = self.scrape_category(category)
            all_quotes.extend(quotes)
            time.sleep(2)  # Be respectful with rate limiting
        
        # Deduplicate by text
        seen = set()
        unique_quotes = []
        for quote in all_quotes:
            if quote['text'] not in seen:
                seen.add(quote['text'])
                unique_quotes.append(quote)
        
        print(f"\nTotal unique quotes: {len(unique_quotes)}")
        return unique_quotes
    
    def save_quotes(self, quotes: List[Dict], filename: str = 'quotes.json'):
        """Save quotes to JSON file"""
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(quotes, f, indent=2, ensure_ascii=False)
        print(f"Saved {len(quotes)} quotes to {filename}")


if __name__ == '__main__':
    scraper = JamesClearScraper()
    quotes = scraper.scrape_all_categories()
    scraper.save_quotes(quotes)
