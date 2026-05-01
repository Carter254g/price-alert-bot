# Setup Guide

## Prerequisites

- Python 3.8 or higher
- A Telegram account

## 1. Clone the Repository

```bash
git clone https://github.com/Carter254g/price-alert-bot.git
cd price-alert-bot
```

## 2. Create a Virtual Environment

```bash
python3 -m venv venv
source venv/bin/activate
```

## 3. Install Dependencies

```bash
pip install -r requirements.txt
```

## 4. Create a Telegram Bot

1. Open Telegram and search for @BotFather
2. Send /newbot and follow the prompts
3. Copy the token BotFather gives you

## 5. Get Your Chat ID

1. Send a message to your new bot
2. Visit this URL in your browser replacing TOKEN with your token:
   https://api.telegram.org/botTOKEN/getUpdates
3. Find the chat id in the response

## 6. Configure Environment Variables

```bash
cp .env.example .env
```

Edit .env and add your token and chat id.

## 7. Add a Target URL

```bash
python bot.py add --url https://jumia.co.ke/product --target 45000
```

## 8. Run the Bot

```bash
python bot.py check
```
