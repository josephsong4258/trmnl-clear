"""
Quote Display Manager
Handles smart display of quotes based on length and e-ink constraints
"""

import json
from typing import List, Dict, Optional
import random
from datetime import datetime


class QuoteDisplayManager:
    """
    Manages quote selection and formatting for e-ink display
    
    TRMNL standard display: 800x480 pixels
    Approximate character limits by layout:
    - Full screen: ~500 characters (ideal: 200-400)
    - Half vertical: ~250 characters (ideal: 100-200)
    - Half horizontal: ~250 characters (ideal: 100-200)
    - Quadrant: ~150 characters (ideal: 50-100)
    """
    
    # Character limits for different layouts
    LIMITS = {
        'full': {'min': 0, 'ideal_max': 800, 'absolute_max': 1200},  # Allow longer quotes
        'half_vertical': {'min': 0, 'ideal_max': 200, 'absolute_max': 300},
        'half_horizontal': {'min': 0, 'ideal_max': 200, 'absolute_max': 300},
        'quadrant': {'min': 0, 'ideal_max': 100, 'absolute_max': 150},
    }

    def __init__(self, quotes_file: str = 'data/quotes.json'):
        """
        Initialize with quotes database

        Args:
            quotes_file: Path to quotes JSON file
        """
        self.quotes_file = quotes_file
        self.quotes = self.load_quotes(quotes_file)
        self.categorize_by_length()

    def load_quotes(self, filename: str) -> List[Dict]:
        """Load quotes from JSON file"""
        try:
            with open(filename, 'r', encoding='utf-8') as f:
                return json.load(f)
        except FileNotFoundError:
            print(f"Quote file {filename} not found")
            return []

    def categorize_by_length(self):
        """Categorize quotes by length for efficient selection"""
        self.by_length = {
            'short': [],      # < 100 chars
            'medium': [],     # 100-250 chars
            'long': [],       # 250-500 chars
            'very_long': [],  # > 500 chars
        }

        for quote in self.quotes:
            length = quote.get('length', len(quote['text']))

            if length < 100:
                self.by_length['short'].append(quote)
            elif length < 250:
                self.by_length['medium'].append(quote)
            elif length < 500:
                self.by_length['long'].append(quote)
            else:
                self.by_length['very_long'].append(quote)

    def select_quote_for_layout(self, layout: str = 'full', random_selection: bool = True) -> Optional[Dict]:
        """
        Select appropriate quote based on display layout

        Args:
            layout: TRMNL layout type (full, half_vertical, half_horizontal, quadrant)
            random_selection: Whether to select randomly or use rotation

        Returns:
            Selected quote dict
        """
        limits = self.LIMITS.get(layout, self.LIMITS['full'])
        ideal_max = limits['ideal_max']

        # Determine which length categories to use
        suitable_quotes = []

        if layout == 'full':
            # FULL SCREEN: Include ALL quotes regardless of length
            suitable_quotes = self.quotes
        elif layout in ['half_vertical', 'half_horizontal']:
            # Prefer short to medium
            suitable_quotes = (
                self.by_length['short'] +
                self.by_length['medium']
            )
        elif layout == 'quadrant':
            # Only short quotes
            suitable_quotes = self.by_length['short']

        if not suitable_quotes:
            return None

        if random_selection:
            return random.choice(suitable_quotes)
        else:
            # Could implement rotation logic here
            return suitable_quotes[0]

    def truncate_quote(self, quote_text: str, max_length: int) -> str:
        """
        Intelligently truncate a quote that's too long

        Tries to break at sentence boundaries
        """
        if len(quote_text) <= max_length:
            return quote_text

        # Try to find last sentence boundary before max_length
        truncated = quote_text[:max_length]

        # Look for last period, exclamation, or question mark
        for char in ['. ', '! ', '? ']:
            last_sentence = truncated.rfind(char)
            if last_sentence > max_length * 0.6:  # At least 60% of desired length
                return quote_text[:last_sentence + 1].strip()

        # If no good sentence break, truncate at word boundary
        last_space = truncated.rfind(' ')
        if last_space > 0:
            return truncated[:last_space] + '...'

        return truncated + '...'

    def format_for_display(self, quote: Dict, layout: str = 'full') -> Dict:
        """
        Format quote for TRMNL display

        Returns formatted data ready for markup template
        """
        text = quote['text']
        limits = self.LIMITS.get(layout, self.LIMITS['full'])

        # For full screen, show entire quote without truncation
        if layout == 'full':
            # Only truncate if EXTREMELY long (over absolute max)
            if len(text) > limits['absolute_max']:
                text = self.truncate_quote(text, limits['absolute_max'])
        else:
            # For other layouts, truncate if needed
            if len(text) > limits['absolute_max']:
                text = self.truncate_quote(text, limits['ideal_max'])

        return {
            'text': text,
            'category': quote.get('category', ''),
            'source': quote.get('source', 'James Clear'),
            'length': len(text),
            'layout': layout,
            'formatted_at': datetime.now().isoformat()
        }

    def get_daily_quote(self, layout: str = 'full') -> Dict:
        """
        Get a random quote without repeats until all quotes have been shown

        Uses deterministic shuffle based on "epoch" (resets every N quotes)
        This ensures no repeats within a cycle, but random order
        """
        # Get suitable quotes for this layout
        suitable_quotes = []

        if layout == 'full':
            suitable_quotes = self.quotes
        elif layout in ['half_vertical', 'half_horizontal']:
            suitable_quotes = self.by_length['short'] + self.by_length['medium']
        elif layout == 'quadrant':
            suitable_quotes = self.by_length['short']

        if not suitable_quotes:
            return None

        # Calculate which "cycle" we're in (resets after showing all quotes)
        minutes_since_epoch = int(datetime.now().timestamp() / 60)
        total_quotes = len(suitable_quotes)

        # Which cycle are we in? (0, 1, 2, ...)
        cycle_number = minutes_since_epoch // total_quotes

        # Which position within this cycle? (0 to total_quotes-1)
        position_in_cycle = minutes_since_epoch % total_quotes

        # Create a shuffled copy using the cycle number as seed
        # Same cycle = same shuffle order, different cycle = different shuffle
        import random
        shuffled = suitable_quotes.copy()
        random.seed(cycle_number)  # Deterministic shuffle per cycle
        random.shuffle(shuffled)
        random.seed()  # Reset seed

        # Get quote at this position
        quote = shuffled[position_in_cycle]

        if quote:
            return self.format_for_display(quote, layout)
        return None

    def get_stats(self) -> Dict:
        """Get statistics about the quote database"""
        return {
            'total_quotes': len(self.quotes),
            'by_length': {
                'short': len(self.by_length['short']),
                'medium': len(self.by_length['medium']),
                'long': len(self.by_length['long']),
                'very_long': len(self.by_length['very_long']),
            },
            'categories': list(set(q.get('category', '') for q in self.quotes)),
        }


if __name__ == '__main__':
    # Example usage
    manager = QuoteDisplayManager()
    print("Quote Database Stats:")
    print(json.dumps(manager.get_stats(), indent=2))

    print("\nDaily quote (full layout):")
    daily = manager.get_daily_quote('full')
    if daily:
        print(f"Text: {daily['text'][:100]}...")
        print(f"Length: {daily['length']} chars")