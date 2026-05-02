# Price Alert Bot

A Python automation tool that monitors product prices and fires instant Telegram alerts when your target price is hit.

## Demo

Add a URL, set a target price, and get a Telegram message the moment the price drops.

## Features

- Monitor any URL for price changes
- Instant Telegram notifications when price drops
- Track multiple URLs at once
- Pause and resume individual targets
- Runs automatically on a schedule
- Clean CLI interface to manage everything
- Summary report after every check

## Tech Stack

- Language: Python 3
- Scraping: BeautifulSoup4, Requests
- Notifications: Telegram Bot API
- Scheduling: APScheduler
- CLI: Typer
- Config: JSON + python-dotenv

## Setup

### 1. Clone the repo

```bash
git clone https://github.com/Carter254g/price-alert-bot.git
cd price-alert-bot
```

### 2. Create a virtual environment

```bash
python3 -m venv venv
source venv/bin/activate
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

### 4. Create a Telegram bot

1. Open Telegram and search for @BotFather
2. Send /newbot and follow the prompts
3. Copy the token BotFather gives you

### 5. Get your Chat ID

1. Send any message to your new bot
2. Visit this URL replacing TOKEN with your token:
   https://api.telegram.org/botTOKEN/getUpdates
3. Find the chat id in the response

### 6. Configure environment variables

```bash
cp .env.example .env
```

Edit .env and add your token and chat ID.

### 7. Test the connection

```bash
python3 bot.py test
```

You should receive a message on Telegram.

## Usage

### Add a URL to monitor

```bash
python3 bot.py add --url "https://example.com/product" --target 5000 --label "My Product"
```

### List all monitored URLs

```bash
python3 bot.py list
```

### Check all URLs once

```bash
python3 bot.py check
```

### Start the scheduler

```bash
python3 bot.py start
```

### Pause a target

```bash
python3 bot.py pause --url "https://example.com/product"
```

### Resume a target

```bash
python3 bot.py resume --url "https://example.com/product"
```

### Remove a target

```bash
python3 bot.py remove --url "https://example.com/product"
```

## How It Works

1. You add a product URL and your target price
2. The bot scrapes the page and extracts the current price
3. If the price is at or below your target it fires a Telegram alert instantly
4. The scheduler runs this check automatically every few hours

## Roadmap

- Email alerts alongside Telegram
- Price history tracking and charts
- Web dashboard to manage targets
- Support for job listing sites
- Docker support for always-on deployment

## Author

Carter - Full-stack developer
GitHub: https://github.com/Carter254g

## License

MIT
