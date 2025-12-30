"""
Newsletter Web Scraper
Scrapes the 3 ideas from the web version of the 3-2-1 newsletter
"""

import requests
from bs4 import BeautifulSoup
import json
import re
from datetime import datetime
from typing import List, Dict


class NewsletterWebScraper:
    BASE_URL = 'https://jamesclear.com/3-2-1'

    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36'
        })

    def get_latest_newsletter_url(self) -> str:
        """Get the URL of the most recent newsletter"""
        try:
            response = self.session.get(self.BASE_URL)
            response.raise_for_status()

            soup = BeautifulSoup(response.text, 'html.parser')

            # Find the first newsletter link (most recent)
            # Look for links that match the pattern /3-2-1/month-day-year
            links = soup.find_all('a', href=re.compile(r'/3-2-1/\w+-\d+-\d+'))

            if links:
                latest_link = links[0]['href']
                if not latest_link.startswith('http'):
                    latest_link = 'https://jamesclear.com' + latest_link
                return latest_link

            return None

        except Exception as e:
            print(f"Error getting latest newsletter: {e}")
            return None

    def extract_ideas_from_newsletter(self, url: str) -> List[str]:
        """
        Extract the 3 ideas from a newsletter page

        The web version has clean HTML structure:
        <h2>3 IDEAS FROM ME</h2>
        <p>I.</p>
        <p>"Quote text..."</p>
        <hr>
        <p>II.</p>
        <p>"Quote text..."</p>
        etc.
        """
        try:
            response = self.session.get(url)
            response.raise_for_status()

            soup = BeautifulSoup(response.text, 'html.parser')
            ideas = []

            # Find the "3 IDEAS FROM ME" heading
            ideas_heading = soup.find('h2', string=re.compile(r'3 IDEAS FROM ME', re.IGNORECASE))

            if not ideas_heading:
                print("Could not find '3 IDEAS FROM ME' section")
                return []

            # Get all content between "3 IDEAS FROM ME" and "2 QUOTES FROM OTHERS"
            current = ideas_heading.find_next_sibling()
            idea_text = []

            while current:
                # Stop when we hit "2 QUOTES FROM OTHERS"
                if current.name == 'h2' and '2 QUOTES' in current.get_text().upper():
                    break

                # Collect paragraph text
                if current.name == 'p':
                    text = current.get_text(strip=True)

                    # Skip the Roman numerals (I., II., III.)
                    if text and not re.match(r'^I{1,3}\.$', text):
                        # Filter out "Share on Twitter" or similar social media mentions
                        if not re.search(r'share on twitter|tweet|click to share', text, re.IGNORECASE):
                            idea_text.append(text)

                # If we hit an <hr>, we've completed an idea
                elif current.name == 'hr' and idea_text:
                    # Join the accumulated text for this idea
                    full_idea = ' '.join(idea_text).strip()

                    # Clean up quotes
                    full_idea = full_idea.strip('"').strip('"').strip('"')

                    # Final filter: Remove any trailing Twitter mentions
                    full_idea = re.sub(r'\s*\(?\s*share on twitter.*$', '', full_idea, flags=re.IGNORECASE).strip()

                    if len(full_idea) > 10:
                        ideas.append(full_idea)

                    idea_text = []  # Reset for next idea

                current = current.find_next_sibling()

            # Don't forget the last idea if there's no final <hr>
            if idea_text:
                full_idea = ' '.join(idea_text).strip()
                full_idea = full_idea.strip('"').strip('"').strip('"')
                full_idea = re.sub(r'\s*\(?\s*share on twitter.*$', '', full_idea, flags=re.IGNORECASE).strip()
                if len(full_idea) > 10:
                    ideas.append(full_idea)

            return ideas[:3]  # Only return first 3

        except Exception as e:
            print(f"Error extracting ideas from {url}: {e}")
            return []

    def get_latest_ideas(self) -> Dict:
        """Get the 3 ideas from the most recent newsletter"""
        url = self.get_latest_newsletter_url()

        if not url:
            print("Could not find latest newsletter")
            return None

        print(f"Scraping latest newsletter: {url}")
        ideas = self.extract_ideas_from_newsletter(url)

        if ideas:
            return {
                'url': url,
                'date': datetime.now().isoformat(),
                'ideas': ideas,
                'count': len(ideas)
            }

        return None

    def scrape_recent_newsletters(self, count: int = 5) -> List[Dict]:
        """Scrape multiple recent newsletters"""
        try:
            response = self.session.get(self.BASE_URL)
            response.raise_for_status()

            soup = BeautifulSoup(response.text, 'html.parser')

            # Find newsletter links
            links = soup.find_all('a', href=re.compile(r'/3-2-1/\w+-\d+-\d+'))

            newsletters = []

            for link in links[:count]:
                url = link['href']
                if not url.startswith('http'):
                    url = 'https://jamesclear.com' + url

                print(f"Scraping: {url}")
                ideas = self.extract_ideas_from_newsletter(url)

                if ideas:
                    newsletters.append({
                        'url': url,
                        'title': link.get_text(strip=True),
                        'ideas': ideas,
                        'scraped_at': datetime.now().isoformat()
                    })

            return newsletters

        except Exception as e:
            print(f"Error scraping recent newsletters: {e}")
            return []

    def scrape_all_newsletters(self) -> List[Dict]:
        """
        Scrape ALL 3-2-1 newsletters going back to 2019

        The newsletters follow a pattern:
        https://jamesclear.com/3-2-1/december-25-2025
        https://jamesclear.com/3-2-1/december-18-2025
        etc.

        Published every Thursday since November 2019
        """
        import time
        from datetime import timedelta

        newsletters = []

        # Start from today and go back to November 2019
        start_date = datetime(2019, 11, 7)  # First 3-2-1 newsletter
        current_date = datetime.now()

        print(f"Scraping newsletters from {start_date.date()} to {current_date.date()}...")
        print("This will take a few minutes (respecting rate limits)...")

        # Generate all Thursday dates
        date = start_date
        urls_to_try = []

        while date <= current_date:
            # 3-2-1 is published on Thursdays (weekday 3)
            if date.weekday() == 3:  # Thursday
                # Format: december-25-2025
                url = f"https://jamesclear.com/3-2-1/{date.strftime('%B').lower()}-{date.day}-{date.year}"
                urls_to_try.append((url, date))
            date += timedelta(days=1)

        print(f"Found {len(urls_to_try)} potential newsletter dates")

        successful = 0
        failed = 0

        for url, date in urls_to_try:
            try:
                # Rate limiting - be respectful
                time.sleep(0.5)  # Half second between requests

                ideas = self.extract_ideas_from_newsletter(url)

                if ideas:
                    newsletters.append({
                        'url': url,
                        'date': date.strftime('%Y-%m-%d'),
                        'ideas': ideas,
                        'scraped_at': datetime.now().isoformat()
                    })
                    successful += 1
                    print(f"✓ {date.strftime('%Y-%m-%d')}: {len(ideas)} ideas")
                else:
                    failed += 1

            except Exception as e:
                failed += 1
                # Don't print errors for every 404 (newsletter might not exist for that date)
                if failed % 10 == 0:
                    print(f"  Checked {successful + failed} dates so far...")

        print(f"\n✅ Successfully scraped {successful} newsletters")
        print(f"   Total ideas: {sum(len(n['ideas']) for n in newsletters)}")

        return newsletters
    def save_newsletter_ideas(self, newsletters: List[Dict], filename: str = 'data/newsletter_ideas.json'):
        """Save newsletter ideas to file"""
        import os
        os.makedirs('data', exist_ok=True)

        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(newsletters, f, indent=2, ensure_ascii=False)
        print(f"Saved {len(newsletters)} newsletters to {filename}")


if __name__ == '__main__':
    scraper = NewsletterWebScraper()

    # Get latest newsletter
    print("Fetching latest newsletter...")
    latest = scraper.get_latest_ideas()

    if latest:
        print(f"\nLatest newsletter ({latest['url']}):")
        print(f"Found {latest['count']} ideas:")
        for i, idea in enumerate(latest['ideas'], 1):
            print(f"\n{i}. {idea[:100]}...")

    # Optionally scrape recent newsletters
    print("\n" + "="*50)
    print("Scraping recent newsletters...")
    recent = scraper.scrape_recent_newsletters(count=3)

    if recent:
        scraper.save_newsletter_ideas(recent)
        print(f"\nScraped {len(recent)} recent newsletters")

        total_ideas = sum(len(n['ideas']) for n in recent)
        print(f"Total ideas extracted: {total_ideas}")