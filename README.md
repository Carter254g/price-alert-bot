# Price Alert Bot

A Python Telegram bot that helps you find products, monitor prices, buy and sell items — all from Telegram.

No tech knowledge needed. Just open Telegram and type a command.

## What It Does

**For Buyers:**
- Search for any product by name
- Filter results by country and price range
- Get real listings from Jiji Kenya
- Set a target price and get alerted automatically when it drops
- Browse items listed for sale by other users

**For Sellers:**
- List any product you want to sell
- Add photos of your item
- Buyers can find and contact you directly on Telegram

## Commands
/search   - Search and monitor a product price
/browse   - Browse listings from Jiji Kenya and local sellers
/sell     - List a product you want to sell
/mylistings - See and manage your active listings
/list     - See your monitored products
/check    - Check all prices right now
/help     - Show all commands
## Tech Stack

- Language: Python 3
- Bot framework: python-telegram-bot
- Scraping: BeautifulSoup4, Requests
- Search: SerpAPI (Google Search)
- Marketplace data: Jiji Kenya scraper
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
2. Visit: https://api.telegram.org/botTOKEN/getUpdates
3. Find the chat id in the response

### 6. Get a SerpAPI key

Sign up free at https://serpapi.com to get your API key.

### 7. Configure environment variables

```bash
cp .env.example .env
```

Edit .env and fill in your values.

### 8. Start the bot

```bash
python3 bot.py telegram
```

Open Telegram and type /start.

## How It Works

1. User types /browse in Telegram
2. Bot asks what they are looking for
3. Bot asks for price range
4. Bot searches Jiji Kenya and local listings
5. Results come back with prices, locations and links
6. User can contact sellers directly or set a price alert

## Roadmap

- Email alerts alongside Telegram
- WhatsApp integration
- More marketplace sources
- Price history charts
- Web dashboard

## Author

Carter - Full-stack developer
GitHub: https://github.com/Carter254g

## License

MIT
