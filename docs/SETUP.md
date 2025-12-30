# Setup Guide

Complete setup instructions for the James Clear TRMNL Plugin.

## Prerequisites

- Python 3.8 or higher
- pip (Python package installer)
- A TRMNL device (order at https://usetrmnl.com)
- Git (for cloning the repository)

## Step 1: Clone the Repository

```bash
git clone https://github.com/josephsong4258/trmnl-james-clear-quotes.git
cd trmnl-james-clear-quotes
```

## Step 2: Install Dependencies

```bash
pip install -r requirements.txt
```

This installs:
- Flask (web server)
- Requests (HTTP library)
- BeautifulSoup4 (HTML parsing)
- Schedule (task scheduling)
- Gunicorn (production server)

## Step 3: Initial Quote Scrape

Build your initial quote database:

```bash
python src/scraper.py
```

This will:
- Visit all 6 James Clear quote pages
- Extract and deduplicate quotes
- Save to `data/quotes.json`
- Take approximately 1-2 minutes

Expected output:
```
Scraping https://jamesclear.com/quote/life...
Found 85 quotes in life
Scraping https://jamesclear.com/quote/atomic-habits...
Found 72 quotes in atomic-habits
...
Total unique quotes: 547
Saved 547 quotes to data/quotes.json
```

## Step 4: Configuration (Optional)

Copy the configuration template:

```bash
cp config/config.json.template config/config.json
```

Edit `config/config.json` to customize settings.

### Configuration Options

```json
{
  "email": {
    "enabled": false,              // Enable email monitoring
    "email": "your-email@gmail.com",
    "password": "app-password",    // Gmail app-specific password
    "imap_server": "imap.gmail.com"
  },
  "trmnl": {
    "plugin_name": "James Clear Quotes",
    "plugin_description": "Daily wisdom from James Clear",
    "plugin_markup_url": "https://your-server.com/plugin"
  },
  "display": {
    "default_layout": "full",
    "rotation_enabled": true,
    "daily_quote": true
  }
}
```

## Step 5: Test Locally

Start the development server:

```bash
python src/server.py
```

The server will start on `http://localhost:5000`

Test the plugin endpoint:

```bash
curl -X POST http://localhost:5000/plugin \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "user_uuid=test"
```

You should receive JSON with HTML markup for all layouts.

### Test Other Endpoints

**Health Check:**
```bash
curl http://localhost:5000/health
```

**Stats:**
```bash
curl http://localhost:5000/stats
```

## Step 6: Deploy to Production

See [DEPLOYMENT.md](DEPLOYMENT.md) for detailed deployment instructions for:
- Railway
- Render
- DigitalOcean
- Docker

## Step 7: Register with TRMNL

1. Deploy your server and get the public URL
2. Go to https://usetrmnl.com/login
3. Navigate to Developer settings
4. Create a new Private Plugin:
   - **Name**: James Clear Quotes
   - **Description**: Daily wisdom from James Clear
   - **Plugin Markup URL**: `https://your-server.com/plugin`
   - **Icon**: Upload a custom icon (optional)

5. Add the plugin to your playlist
6. Configure refresh interval (recommended: 30-60 minutes)

## Optional: Newsletter Integration

You have two options for capturing new quotes from the 3-2-1 newsletter:

### Option A: Email Monitoring

1. Subscribe to the newsletter at https://jamesclear.com/3-2-1

2. For Gmail, create an app-specific password:
   - Go to https://myaccount.google.com/apppasswords
   - Select "Mail" and "Other"
   - Generate password

3. Update `config/config.json`:
   ```json
   {
     "email": {
       "enabled": true,
       "email": "your-email@gmail.com",
       "password": "generated-app-password"
     }
   }
   ```

4. Run the updater:
   ```bash
   python src/updater.py
   ```

### Option B: Webhook (Recommended)

More reliable than email monitoring. Set up automation with Zapier or Make:

**Using Zapier:**

1. Create a new Zap
2. **Trigger**: Gmail - New Email Matching Search
   - Search: `from:james@jamesclear.com subject:"3-2-1"`
3. **Action**: Code by Zapier - Run Python
   - Parse email body and extract quotes
4. **Action**: Webhooks by Zapier - POST
   - URL: `https://your-server.com/webhook/newsletter`
   - Payload Type: JSON
   - Data:
     ```json
     {
       "quotes": [
         "{{extracted_quote_1}}",
         "{{extracted_quote_2}}",
         "{{extracted_quote_3}}"
       ]
     }
     ```

See [NEWSLETTER_INTEGRATION.md](NEWSLETTER_INTEGRATION.md) for detailed webhook setup.

## Automated Updates

To keep quotes fresh, run the updater as a background service:

### On Linux (systemd)

Create `/etc/systemd/system/trmnl-quotes-updater.service`:

```ini
[Unit]
Description=TRMNL James Clear Quote Updater
After=network.target

[Service]
Type=simple
User=youruser
WorkingDirectory=/path/to/trmnl-james-clear-quotes
ExecStart=/usr/bin/python3 src/updater.py
Restart=always

[Install]
WantedBy=multi-user.target
```

Enable and start:
```bash
sudo systemctl enable trmnl-quotes-updater
sudo systemctl start trmnl-quotes-updater
```

### Using Screen (Simple Alternative)

```bash
screen -S trmnl-updater
python src/updater.py
# Press Ctrl+A, then D to detach
```

Reattach later with:
```bash
screen -r trmnl-updater
```

## Troubleshooting

### Server won't start

**Error**: `Address already in use`
- **Solution**: Port 5000 is taken. Kill the process or use a different port:
  ```bash
  python src/server.py --port 5001
  ```

**Error**: `ModuleNotFoundError`
- **Solution**: Install dependencies:
  ```bash
  pip install -r requirements.txt
  ```

### No quotes in database

**Error**: `quotes.json` is empty or missing
- **Solution**: Run the scraper:
  ```bash
  python src/scraper.py
  ```

### Email monitoring not working

**Error**: Authentication failed
- **Solution**: 
  1. Verify email/password in config
  2. For Gmail, enable "Less secure app access" or use app-specific password
  3. Check IMAP is enabled in email settings

**Error**: No quotes extracted
- **Solution**: The email parser may need updating. Check newsletter format hasn't changed.

### TRMNL can't connect to plugin

**Error**: Connection refused
- **Solution**: 
  1. Verify server is running: `curl http://localhost:5000/health`
  2. Check firewall allows inbound connections
  3. Ensure URL in TRMNL settings is correct and publicly accessible

### Quotes too long/short for display

- **Solution**: Adjust limits in `src/display_manager.py`:
  ```python
  LIMITS = {
      'full': {'min': 0, 'ideal_max': 400, 'absolute_max': 600},
      # Adjust these values as needed
  }
  ```

## Next Steps

- [Deploy to production](DEPLOYMENT.md)
- [Set up newsletter integration](NEWSLETTER_INTEGRATION.md)
- [Customize the plugin](DEVELOPMENT.md)
- [View API reference](API.md)

