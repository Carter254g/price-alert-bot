import os
import logging
from dotenv import load_dotenv
from telegram import Update
from telegram.ext import Application, CommandHandler, ContextTypes, ConversationHandler, MessageHandler, filters
from src.targets import add_target, load_targets
from src.search import search_products, get_countries_text, get_country
from src.scraper import scrape

load_dotenv()

logging.basicConfig(level=logging.WARNING)

WAITING_FOR_SEARCH, WAITING_FOR_COUNTRY, WAITING_FOR_PICK, WAITING_FOR_PRICE = range(4)

user_sessions = {}

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "Hi! I am your Price Alert Bot.\n\n"
        "Search for any product and I will alert you on Telegram when the price drops to your target.\n\n"
        "Commands:\n"
        "/search - Search for a product to monitor\n"
        "/list - See all your monitored products\n"
        "/check - Check all prices now\n"
        "/remove - Remove a product\n"
        "/help - Show this message"
    )

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "Here is what I can do:\n\n"
        "/search - Search for any product by name\n"
        "/list - See all monitored products\n"
        "/check - Check all prices right now\n"
        "/remove - Stop monitoring a product\n"
        "/help - Show this message"
    )

async def search_start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "What product are you looking for?\n\n"
        "For example: PS5, iPhone 15, Nike Air Max, Laptop"
    )
    return WAITING_FOR_SEARCH

async def get_query(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.message.text.strip()
    user_id = update.effective_user.id
    user_sessions[user_id] = {"query": query}
    await update.message.reply_text(get_countries_text())
    return WAITING_FOR_COUNTRY

async def get_country_choice(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    choice = update.message.text.strip()
    country = get_country(choice)

    if not country:
        await update.message.reply_text("Please send a valid number from the list.")
        return WAITING_FOR_COUNTRY

    session = user_sessions[user_id]
    session["country"] = country
    query = session["query"]

    await update.message.reply_text(
        f"Searching for {query} in {country['name']}..."
    )

    results = search_products(query, country["gl"])

    if not results:
        await update.message.reply_text(
            "No results found. Try a different search term."
        )
        return ConversationHandler.END

    session["results"] = results

    message = f"Top results for {query} in {country['name']}:\n\n"
    for i, r in enumerate(results, 1):
        message += f"{i}. {r['title']}\n"
        message += f"   Price: {r['price']}\n"
        message += f"   Store: {r['source']}\n\n"

    message += "Reply with the number of the product you want to monitor."
    await update.message.reply_text(message)
    return WAITING_FOR_PICK

async def pick_product(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    session = user_sessions.get(user_id, {})
    results = session.get("results", [])

    try:
        choice = int(update.message.text.strip())
        if choice < 1 or choice > len(results):
            await update.message.reply_text(f"Please send a number between 1 and {len(results)}")
            return WAITING_FOR_PICK

        selected = results[choice - 1]
        session["selected"] = selected

        await update.message.reply_text(
            f"Great choice!\n\n"
            f"Product: {selected['title']}\n"
            f"Current price: {selected['price']}\n"
            f"Store: {selected['source']}\n\n"
            f"What is your target price?\n"
            f"I will alert you when the price drops to this amount or below."
        )
        return WAITING_FOR_PRICE

    except ValueError:
        await update.message.reply_text("Please send a valid number.")
        return WAITING_FOR_PICK

async def set_price(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    session = user_sessions.get(user_id, {})
    selected = session.get("selected", {})
    country = session.get("country", {})

    try:
        target_price = float(update.message.text.strip().replace(",", ""))
        url = selected.get("link", "")
        title = selected.get("title", "Unknown")

        if url:
            add_target(url, target_price, title)
            await update.message.reply_text(
                f"Added successfully!\n\n"
                f"Product: {title}\n"
                f"Country: {country.get('name', 'Unknown')}\n"
                f"Current price: {selected['price']}\n"
                f"Your target: {target_price}\n\n"
                f"I will alert you when the price drops to {target_price} or below.\n\n"
                f"Use /check to check now or wait for automatic checks."
            )
        else:
            await update.message.reply_text(
                f"Monitoring set for {title} at target price {target_price}."
            )

        user_sessions.pop(user_id, None)
        return ConversationHandler.END

    except ValueError:
        await update.message.reply_text("Please send a valid number. For example: 50000")
        return WAITING_FOR_PRICE

async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_sessions.pop(update.effective_user.id, None)
    await update.message.reply_text("Cancelled.")
    return ConversationHandler.END

async def list_targets(update: Update, context: ContextTypes.DEFAULT_TYPE):
    targets = load_targets()
    if not targets:
        await update.message.reply_text(
            "You have no products being monitored.\n\nUse /search to find a product."
        )
        return
    message = "Your monitored products:\n\n"
    for i, t in enumerate(targets, 1):
        status = "active" if t.get("active", True) else "paused"
        last = t.get("last_price") or "not checked yet"
        message += (
            f"{i}. {t['label'] or t['url']}\n"
            f"   Target: {t['target_price']}\n"
            f"   Last price: {last}\n"
            f"   Status: {status}\n\n"
        )
    await update.message.reply_text(message)

async def check_now(update: Update, context: ContextTypes.DEFAULT_TYPE):
    targets = load_targets()
    if not targets:
        await update.message.reply_text("No products to check. Use /search to add one.")
        return
    await update.message.reply_text(f"Checking {len(targets)} product(s)...")
    for target in targets:
        if not target.get("active", True):
            continue
        result = scrape(target["url"])
        if not result or result["price"] is None:
            await update.message.reply_text(
                f"Could not get price for: {target['label'] or target['url']}"
            )
            continue
        current = result["price"]
        goal = target["target_price"]
        label = target["label"] or target["url"]
        if current <= goal:
            await update.message.reply_text(
                f"Price Alert!\n\n"
                f"Product: {label}\n"
                f"Current price: {current}\n"
                f"Your target: {goal}\n\n"
                f"URL: {target['url']}"
            )
        else:
            await update.message.reply_text(
                f"No alert for {label}\n"
                f"Current price: {current} | Your target: {goal}"
            )

async def remove_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    targets = load_targets()
    if not targets:
        await update.message.reply_text("You have no products being monitored.")
        return
    message = "Send the number of the product to remove:\n\n"
    for i, t in enumerate(targets, 1):
        message += f"{i}. {t['label'] or t['url']}\n"
    await update.message.reply_text(message)

def run_bot():
    token = os.getenv("TELEGRAM_BOT_TOKEN")
    app = Application.builder().token(token).build()

    search_handler = ConversationHandler(
        entry_points=[CommandHandler("search", search_start)],
        states={
            WAITING_FOR_SEARCH: [MessageHandler(filters.TEXT & ~filters.COMMAND, get_query)],
            WAITING_FOR_COUNTRY: [MessageHandler(filters.TEXT & ~filters.COMMAND, get_country_choice)],
            WAITING_FOR_PICK: [MessageHandler(filters.TEXT & ~filters.COMMAND, pick_product)],
            WAITING_FOR_PRICE: [MessageHandler(filters.TEXT & ~filters.COMMAND, set_price)],
        },
        fallbacks=[CommandHandler("cancel", cancel)],
    )

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("help", help_command))
    app.add_handler(CommandHandler("list", list_targets))
    app.add_handler(CommandHandler("check", check_now))
    app.add_handler(CommandHandler("remove", remove_command))
    app.add_handler(search_handler)

    print("Bot is running. Open Telegram and type /start to begin.")
    app.run_polling()
