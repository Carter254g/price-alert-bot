import requests
import os
from dotenv import load_dotenv

load_dotenv()

TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")

def send_message(message):
    if not TELEGRAM_BOT_TOKEN or not TELEGRAM_CHAT_ID:
        print("Telegram credentials not configured.")
        return False

    url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
    payload = {
        "chat_id": TELEGRAM_CHAT_ID,
        "text": message,
        "parse_mode": "HTML",
    }

    try:
        response = requests.post(url, json=payload, timeout=10)
        response.raise_for_status()
        print("Telegram message sent successfully.")
        return True
    except requests.RequestException as e:
        print(f"Failed to send Telegram message: {e}")
        return False

def send_price_alert(title, url, current_price, target_price):
    message = (
        f"Price Alert\n\n"
        f"<b>{title}</b>\n\n"
        f"Current price: <b>{current_price}</b>\n"
        f"Your target: <b>{target_price}</b>\n\n"
        f"<a href='{url}'>View product</a>"
    )
    return send_message(message)

def send_test_message():
    return send_message("Price Alert Bot is connected and running.")
