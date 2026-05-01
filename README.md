# Price Alert Bot

A Python automation tool that monitors product prices and job listings, then fires instant Telegram alerts when your target price is hit or new listings appear.

## Features

- Monitor any URL for price changes
- Instant Telegram notifications when price drops
- Track multiple URLs at once
- Runs automatically on a schedule
- Simple CLI interface to manage alerts
- Supports Jumia, Amazon, and any site with structured pricing

## Tech Stack

- Language: Python 3
- Scraping: BeautifulSoup4, Requests
- Notifications: Telegram Bot API
- Scheduling: APScheduler
- CLI: Typer
- Config: JSON + python-dotenv

## Project Structure
price-alert-bot/
├── src/
│   ├── scraper.py        # Web scraping logic
│   ├── telegram.py       # Telegram bot integration
│   ├── scheduler.py      # Automated scheduling
│   └── cli.py            # CLI interface
├── config/
│   └── targets.json      # URLs and target prices
├── logs/                 # Run logs
├── bot.py                # Entry point
├── requirements.txt      # Dependencies
└── .env.example          # Environment variable template
## Usage

```bash
# Add a URL to monitor
python bot.py add --url https://jumia.co.ke/product --target 45000

# List all monitored URLs
python bot.py list

# Run the bot once
python bot.py check

# Start the scheduler
python bot.py start
```

## Setup

See SETUP.md for full installation instructions.

## Roadmap

- Email alerts alongside Telegram
- Price history chart
- Web dashboard to manage targets
- Support for job listing sites

## Author

Carter - Full-stack developer
GitHub: https://github.com/Carter254g

## License

MIT
