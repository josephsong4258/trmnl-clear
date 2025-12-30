"""
Local Newsletter Scraper
Run this locally to scrape all newsletters and save to data/quotes.json
"""

from src.newsletter_scraper import NewsletterWebScraper
import json
from datetime import datetime

print("🚀 Starting newsletter scraper...")
print("⏱️  This will take 5-10 minutes...\n")

# Create scraper
scraper = NewsletterWebScraper()

# Scrape ALL newsletters
newsletters = scraper.scrape_all_newsletters()

print(f"\n✅ Scraped {len(newsletters)} newsletters")
print(f"📊 Total ideas: {sum(len(n['ideas']) for n in newsletters)}")

# Load existing quotes
print("\n📂 Loading existing quotes...")
with open('../data/quotes.json', 'r', encoding='utf-8') as f:
    quotes = json.load(f)

print(f"   Found {len(quotes)} existing quotes")

# Add newsletter ideas
added = 0
for newsletter in newsletters:
    for idea in newsletter['ideas']:
        # Check if already exists
        if not any(q['text'] == idea for q in quotes):
            quotes.append({
                'text': idea,
                'category': '3-2-1-newsletter',
                'source': 'James Clear - 3-2-1 Newsletter',
                'length': len(idea),
                'scraped_at': datetime.now().isoformat()
            })
            added += 1

print(f"\n✨ Added {added} new newsletter quotes")

# Save
print("\n💾 Saving to data/quotes.json...")
with open('../data/quotes.json', 'w', encoding='utf-8') as f:
    json.dump(quotes, f, indent=2, ensure_ascii=False)

print(f"\n✅ COMPLETE!")
print(f"📊 Total quotes: {len(quotes)}")
print(f"\nNext steps:")
print(f"  1. git add data/quotes.json")
print(f"  2. git commit -m 'Add all newsletter quotes'")
print(f"  3. git push")