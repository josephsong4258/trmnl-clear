"""
Email Monitor for James Clear's 3-2-1 Newsletter
Monitors email inbox for Tuesday newsletter and extracts the 3 quotes from James
"""

import imaplib
import email
from email.header import decode_header
import re
from datetime import datetime
from typing import List, Dict, Optional
import json


class NewsletterMonitor:
    """Monitor email for James Clear's 3-2-1 newsletter"""
    
    def __init__(self, email_address: str, password: str, imap_server: str = 'imap.gmail.com'):
        """
        Initialize email monitor
        
        Args:
            email_address: Your email address
            password: App-specific password (not your regular password)
            imap_server: IMAP server address
        """
        self.email_address = email_address
        self.password = password
        self.imap_server = imap_server
    
    def connect(self) -> imaplib.IMAP4_SSL:
        """Connect to email server"""
        mail = imaplib.IMAP4_SSL(self.imap_server)
        mail.login(self.email_address, self.password)
        return mail
    
    def extract_quotes_from_email(self, email_body: str) -> List[str]:
        """
        Extract the 3 ideas from James Clear from the newsletter
        
        The newsletter format is:
        3 IDEAS FROM ME
        I. "First quote"
        II. "Second quote"
        III. "Third quote"
        """
        quotes = []
        
        # Look for the "3 IDEAS FROM ME" section
        ideas_pattern = r'3 IDEAS FROM ME(.*?)(?:2 QUOTES FROM OTHERS|$)'
        ideas_match = re.search(ideas_pattern, email_body, re.DOTALL | re.IGNORECASE)
        
        if ideas_match:
            ideas_section = ideas_match.group(1)
            
            # Extract individual ideas (I., II., III.)
            idea_pattern = r'(?:I{1,3}\.)\s*["""]([^"""]+)["""]'
            found_quotes = re.findall(idea_pattern, ideas_section)
            
            for quote in found_quotes:
                cleaned = quote.strip()
                if len(cleaned) > 10:  # Basic validation
                    quotes.append(cleaned)
        
        return quotes
    
    def get_recent_newsletters(self, days: int = 7) -> List[Dict]:
        """
        Get recent 3-2-1 newsletters
        
        Args:
            days: Number of days to look back
            
        Returns:
            List of newsletter data with extracted quotes
        """
        try:
            mail = self.connect()
            mail.select('INBOX')
            
            # Search for emails from James Clear
            # Adjust the sender email as needed
            search_criteria = '(FROM "james@jamesclear.com" SUBJECT "3-2-1")'
            _, message_numbers = mail.search(None, search_criteria)
            
            newsletters = []
            
            for num in message_numbers[0].split()[-10:]:  # Get last 10
                _, msg_data = mail.fetch(num, '(RFC822)')
                email_body = msg_data[0][1]
                email_message = email.message_from_bytes(email_body)
                
                # Get email date
                date_str = email_message['Date']
                # Parse date (simplified)
                
                # Get email body
                body = self.get_email_body(email_message)
                
                # Extract quotes
                quotes = self.extract_quotes_from_email(body)
                
                if quotes:
                    newsletters.append({
                        'date': date_str,
                        'subject': email_message['Subject'],
                        'quotes': quotes,
                        'extracted_at': datetime.now().isoformat()
                    })
            
            mail.close()
            mail.logout()
            
            return newsletters
            
        except Exception as e:
            print(f"Error monitoring email: {e}")
            return []
    
    def get_email_body(self, email_message) -> str:
        """Extract text body from email message"""
        body = ""
        
        if email_message.is_multipart():
            for part in email_message.walk():
                if part.get_content_type() == "text/plain":
                    try:
                        body = part.get_payload(decode=True).decode()
                        break
                    except:
                        pass
        else:
            try:
                body = email_message.get_payload(decode=True).decode()
            except:
                pass
        
        return body
    
    def save_newsletter_quotes(self, newsletters: List[Dict], filename: str = 'newsletter_quotes.json'):
        """Save newsletter quotes to file"""
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(newsletters, f, indent=2, ensure_ascii=False)


# Alternative: RSS/Webhook approach (recommended)
class WebhookReceiver:
    """
    Alternative to email monitoring: Set up a webhook that receives
    newsletter content via services like Zapier or Make
    """
    
    def __init__(self, webhook_url: str):
        self.webhook_url = webhook_url
    
    def process_webhook_data(self, data: Dict) -> List[str]:
        """Process incoming webhook data and extract quotes"""
        # Implementation depends on how the webhook sends data
        pass


# Example configuration template
EMAIL_CONFIG_TEMPLATE = {
    'email': 'your-email@gmail.com',
    'password': 'your-app-specific-password',  # Generate this in Gmail settings
    'imap_server': 'imap.gmail.com',
    'check_interval_hours': 24,  # Check daily for new newsletters
}
