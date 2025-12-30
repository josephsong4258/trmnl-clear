# TRMNL James Clear Quotes

> Daily wisdom from James Clear on your TRMNL e-ink display

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![Flask](https://img.shields.io/badge/flask-3.0-green.svg)](https://flask.palletsprojects.com/)

A beautiful TRMNL plugin that displays rotating quotes from James Clear, author of *Atomic Habits*. Automatically scrapes quotes from his website and integrates with the weekly 3-2-1 newsletter.

## ✨ Features

- 📚 **500+ Curated Quotes** - Automatically scraped from jamesclear.com
- 📧 **Newsletter Integration** - Captures new quotes from the weekly 3-2-1 Thursday newsletter
- 📏 **Smart Display Logic** - Intelligently handles variable quote lengths for optimal e-ink display
- 🔄 **Daily Rotation** - Consistent quote throughout the day using date-based seeding
- 📱 **All TRMNL Layouts** - Full screen, half vertical, half horizontal, and quadrant support
- 🚀 **Easy Deployment** - One-click deploy to Railway, Render, or run on your own server

## 🖼️ Screenshots

*Coming soon - add your TRMNL display photos here!*

## 🚀 Quick Start

### Prerequisites

- Python 3.8 or higher
- A TRMNL device
- (Optional) Email account for newsletter monitoring

### Installation

1. **Clone the repository**
   ```bash
   git clone https://github.com/josephsong4258/trmnl-james-clear-quotes.git
   cd trmnl-james-clear-quotes
   ```

2. **Run the quick start script**
   ```bash
   chmod +x quickstart.sh
   ./quickstart.sh
   ```

3. **Start the server**
   ```bash
   python3 src/server.py
   ```

4. **Test it locally**
   ```bash
   curl -X POST http://localhost:5000/plugin -d 'user_uuid=test'
   ```

### Deploy to Production

See [DEPLOYMENT.md](docs/DEPLOYMENT.md) for detailed instructions on deploying to:
- Railway (recommended - easiest)
- Render
- DigitalOcean
- Docker

## 📖 Documentation

- [**Setup Guide**](docs/SETUP.md) - Detailed installation and configuration
- [**Deployment Guide**](docs/DEPLOYMENT.md) - Deploy to various platforms
- [**API Reference**](docs/API.md) - Plugin endpoints and webhook integration
- [**Newsletter Integration**](docs/NEWSLETTER_INTEGRATION.md) - Capture new quotes from 3-2-1 Thursday

## 🎯 How It Works

```
┌─────────────────────┐
│   TRMNL Device      │  Requests quote every X minutes
│    (E-ink)          │
└──────┬──────────────┘
       │
       ▼
┌─────────────────────┐
│   Flask Server      │  Selects appropriate quote
│   (Plugin API)      │  based on display layout
└──────┬──────────────┘
       │
       ▼
┌─────────────────────┐
│  Display Manager    │  Smart length handling
│  (Quote Selection)  │  & intelligent truncation
└──────┬──────────────┘
       │
       ▼
┌─────────────────────┐
│  Quote Database     │  500+ quotes from:
│   (quotes.json)     │  • Website scraper (6 categories)
└─────────────────────┘  • Newsletter web scraper (weekly)
```

## 📝 Configuration

Copy the template and customize:

```bash
cp config/config.json.template config/config.json
```

### Newsletter Integration

The plugin automatically checks for new 3-2-1 newsletters by scraping the web version (no email credentials needed!):

**Automatic Web Scraping** (recommended - built-in)
- Runs automatically via `updater.py`
- Scrapes https://jamesclear.com/3-2-1 for latest newsletter
- Extracts only the "3 IDEAS FROM ME" section
- No configuration needed!

**Manual Webhook** (alternative)
- Set up Zapier/Make to POST to `/webhook/newsletter`
- Useful if you want immediate updates
- See [docs/NEWSLETTER_INTEGRATION.md](docs/NEWSLETTER_INTEGRATION.md)

**Email Monitoring** (deprecated - complex)
- Old approach requiring email credentials
- Web scraping is much simpler and more reliable

## 🎨 Quote Length Strategy

The plugin intelligently matches quotes to display layouts:

| Layout | Character Range | Strategy |
|--------|----------------|----------|
| Full Screen | **All lengths** | **ALL quotes included** - Dynamic font sizing |
| Half Vertical | 100-300 chars | Short to medium quotes |
| Half Horizontal | 100-300 chars | Short to medium quotes |
| Quadrant | 50-150 chars | Short quotes only |

**Full Screen Display:**
- Short quotes (< 150 chars): Large font (1.4em)
- Medium quotes (150-300 chars): Medium font (1.2em)
- Long quotes (300-600 chars): Normal font (1.0em)
- Very long quotes (> 600 chars): Small font (0.85em)

The full screen layout shows the complete quote without truncation, automatically adjusting font size for readability.

## 🛠️ Project Structure

```
trmnl-james-clear-quotes/
├── src/                    # Source code
│   ├── scraper.py         # Website quote scraper
│   ├── email_monitor.py   # Newsletter email monitoring
│   ├── display_manager.py # Smart quote selection & formatting
│   ├── server.py          # Flask plugin server
│   └── updater.py         # Scheduled quote updates
├── config/                 # Configuration files
│   └── config.json.template
├── docs/                   # Documentation
│   ├── SETUP.md
│   ├── DEPLOYMENT.md
│   ├── API.md
│   ├── NEWSLETTER_INTEGRATION.md
│   └── DEVELOPMENT.md
├── scripts/                # Utility scripts
│   └── quickstart.sh
├── docker/                 # Docker configuration
│   ├── Dockerfile
│   └── docker-compose.yml
├── .github/                # GitHub workflows
│   └── workflows/
├── tests/                  # Test files (coming soon)
├── .gitignore
├── LICENSE
├── README.md
└── requirements.txt
```

## 🤝 Contributing

Contributions welcome! Please read [CONTRIBUTING.md](CONTRIBUTING.md) for details.

Some ideas for contributions:
- [ ] Better quote parsing from website
- [ ] More robust email extraction
- [ ] Additional quote sources (Twitter, Instagram)
- [ ] User preference for quote categories
- [ ] Quote favoriting system
- [ ] Analytics dashboard
- [ ] Unit tests

## 📊 Stats

- **500+** Unique quotes
- **6** Quote categories
- **4** Display layouts supported
- **Weekly** automatic updates

## 🙏 Credits

- Quotes by [James Clear](https://jamesclear.com)
- Built for [TRMNL](https://usetrmnl.com) e-ink displays
- Inspired by the [3-2-1 Newsletter](https://jamesclear.com/3-2-1)

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## ⚠️ Disclaimer

This is an unofficial plugin and is not affiliated with, endorsed by, or connected to James Clear or his team. All quotes remain the intellectual property of James Clear. This plugin is for personal use only.

---

**Enjoying the plugin?** ⭐ Star this repo and share it with other TRMNL users!

**Questions?** Open an [issue](https://github.com/josephsong4258/trmnl-james-clear-quotes/issues)