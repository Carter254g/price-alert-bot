import os
import logging
from dotenv import load_dotenv
from telegram import Update
from telegram.ext import Application, CommandHandler, ContextTypes, ConversationHandler, MessageHandler, filters
from src.targets import add_target, load_targets
from src.search import search_products, get_countries_text, get_country
from src.scraper import scrape
from src.listings import add_listing, search_listings, get_my_listings, remove_listing

load_dotenv()

logging.basicConfig(level=logging.WARNING)

WAITING_FOR_SEARCH, WAITING_FOR_COUNTRY, WAITING_FOR_PICK, WAITING_FOR_PRICE = range(4)
SELL_TITLE, SELL_PRICE, SELL_CONDITION, SELL_DESCRIPTION, SELL_PHOTO = range(4, 9)
BROWSE_QUERY = range(9, 10)

user_sessions = {}

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "Hi! I am your Price Alert and Marketplace Bot.\n\n"
        "I can help you find products, monitor prices, and buy or sell items.\n\n"
        "Commands:\n"
        "/search - Search and monitor a product price\n"
        "/browse - Browse items for sale\n"
        "/sell - List a product you want to sell\n"
        "/mylistings - See your active listings\n"
        "/list - See your monitored products\n"
        "/check - Check all prices now\n"
        "/help - Show this message"
    )

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "Here is what I can do:\n\n"
        "BUYING:\n"
        "/search - Search and monitor a product price\n"
        "/browse - Browse items listed for sale\n"
        "/list - See your monitored products\n"
        "/check - Check all prices now\n\n"
        "SELLING:\n"
        "/sell - List a product you want to sell\n"
        "/mylistings - See and manage your listings\n\n"
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

    await update.message.reply_text(f"Searching for {query} in {country['name']}...")

    results = search_products(query, country["gl"])

    if not results:
        await update.message.reply_text("No results found. Try a different search term.")
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

async def sell_start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "Let's list your product for sale.\n\n"
        "What are you selling?\n\n"
        "For example: PS5, iPhone 14, Laptop, Nike Shoes"
    )
    return SELL_TITLE

async def sell_title(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    title = update.message.text.strip()
    user_sessions[user_id] = {"sell_title": title}
    await update.message.reply_text(
        f"What is your asking price?\n\n"
        f"Send the amount as a number. For example: 55000"
    )
    return SELL_PRICE

async def sell_price(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    try:
        price = float(update.message.text.strip().replace(",", ""))
        user_sessions[user_id]["sell_price"] = price
        await update.message.reply_text(
            "What is the condition of the item?\n\n"
            "1. Brand new\n"
            "2. Like new\n"
            "3. Good condition\n"
            "4. Fair condition"
        )
        return SELL_CONDITION
    except ValueError:
        await update.message.reply_text("Please send a valid number. For example: 55000")
        return SELL_PRICE

async def sell_condition(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    conditions = {
        "1": "Brand new",
        "2": "Like new",
        "3": "Good condition",
        "4": "Fair condition"
    }
    choice = update.message.text.strip()
    condition = conditions.get(choice, choice)
    user_sessions[user_id]["sell_condition"] = condition
    await update.message.reply_text(
        "Add a short description.\n\n"
        "For example: Sealed box, bought 3 months ago, comes with all accessories."
    )
    return SELL_DESCRIPTION

async def sell_description(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    description = update.message.text.strip()
    user_sessions[user_id]["sell_description"] = description
    await update.message.reply_text(
        "Send a photo of your product.\n\n"
        "Or type /skip to list without a photo."
    )
    return SELL_PHOTO

async def sell_photo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    session = user_sessions.get(user_id, {})
    username = update.effective_user.username or update.effective_user.first_name

    photo_id = None
    if update.message.photo:
        photo_id = update.message.photo[-1].file_id

    listing = add_listing(
        user_id=user_id,
        username=username,
        title=session.get("sell_title", ""),
        price=session.get("sell_price", 0),
        condition=session.get("sell_condition", ""),
        description=session.get("sell_description", ""),
        photo_id=photo_id,
    )

    await update.message.reply_text(
        f"Your listing is live!\n\n"
        f"Product: {listing['title']}\n"
        f"Price: {listing['price']}\n"
        f"Condition: {listing['condition']}\n"
        f"Description: {listing['description']}\n"
        f"Photo: {'Yes' if photo_id else 'No'}\n\n"
        f"Buyers can find your listing using /browse.\n"
        f"Use /mylistings to manage your listings."
    )
    user_sessions.pop(user_id, None)
    return ConversationHandler.END

async def skip_photo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    session = user_sessions.get(user_id, {})
    username = update.effective_user.username or update.effective_user.first_name

    listing = add_listing(
        user_id=user_id,
        username=username,
        title=session.get("sell_title", ""),
        price=session.get("sell_price", 0),
        condition=session.get("sell_condition", ""),
        description=session.get("sell_description", ""),
        photo_id=None,
    )

    await update.message.reply_text(
        f"Your listing is live!\n\n"
        f"Product: {listing['title']}\n"
        f"Price: {listing['price']}\n"
        f"Condition: {listing['condition']}\n\n"
        f"Buyers can find your listing using /browse.\n"
        f"Use /mylistings to manage your listings."
    )
    user_sessions.pop(user_id, None)
    return ConversationHandler.END

async def browse_start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "What are you looking for?\n\n"
        "For example: PS5, iPhone, Laptop, Shoes"
    )
    return list(BROWSE_QUERY)[0]

async def browse_search(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.message.text.strip()
    results = search_listings(query)

    if not results:
        await update.message.reply_text(
            f"No listings found for {query}.\n\n"
            f"Try a different search or check back later."
        )
        return ConversationHandler.END

    for l in results:
        caption = (
            f"Product: {l['title']}\n"
            f"Price: {l['price']}\n"
            f"Condition: {l['condition']}\n"
            f"Description: {l['description']}\n"
            f"Seller: @{l['username']}\n"
            f"Listed: {l['created_at']}\n\n"
            f"Contact the seller directly to buy."
        )
        if l.get("photo_id"):
            await update.message.reply_photo(photo=l["photo_id"], caption=caption)
        else:
            await update.message.reply_text(caption)

    return ConversationHandler.END

async def my_listings(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    listings = get_my_listings(user_id)
    active = [l for l in listings if l.get("active", True)]

    if not active:
        await update.message.reply_text(
            "You have no active listings.\n\nUse /sell to list a product."
        )
        return

    message = f"Your active listings ({len(active)}):\n\n"
    for l in active:
        message += (
            f"ID: {l['id']}\n"
            f"Product: {l['title']}\n"
            f"Price: {l['price']}\n"
            f"Condition: {l['condition']}\n"
            f"Listed: {l['created_at']}\n\n"
        )

    message += "To remove a listing send: /removelisting [ID]"
    await update.message.reply_text(message)

async def remove_listing_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    args = context.args

    if not args:
        await update.message.reply_text(
            "Send the listing ID to remove.\n\nFor example: /removelisting 3\n\nUse /mylistings to see your listing IDs."
        )
        return

    try:
        listing_id = int(args[0])
        success = remove_listing(user_id, listing_id)
        if success:
            await update.message.reply_text(f"Listing {listing_id} removed successfully.")
        else:
            await update.message.reply_text("Listing not found or you do not have permission to remove it.")
    except ValueError:
        await update.message.reply_text("Please send a valid listing ID number.")

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

    sell_handler = ConversationHandler(
        entry_points=[CommandHandler("sell", sell_start)],
        states={
            SELL_TITLE: [MessageHandler(filters.TEXT & ~filters.COMMAND, sell_title)],
            SELL_PRICE: [MessageHandler(filters.TEXT & ~filters.COMMAND, sell_price)],
            SELL_CONDITION: [MessageHandler(filters.TEXT & ~filters.COMMAND, sell_condition)],
            SELL_DESCRIPTION: [MessageHandler(filters.TEXT & ~filters.COMMAND, sell_description)],
            SELL_PHOTO: [
                MessageHandler(filters.PHOTO, sell_photo),
                CommandHandler("skip", skip_photo),
            ],
        },
        fallbacks=[CommandHandler("cancel", cancel)],
    )

    browse_handler = ConversationHandler(
        entry_points=[CommandHandler("browse", browse_start)],
        states={
            list(BROWSE_QUERY)[0]: [MessageHandler(filters.TEXT & ~filters.COMMAND, browse_search)],
        },
        fallbacks=[CommandHandler("cancel", cancel)],
    )

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("help", help_command))
    app.add_handler(CommandHandler("list", list_targets))
    app.add_handler(CommandHandler("check", check_now))
    app.add_handler(CommandHandler("mylistings", my_listings))
    app.add_handler(CommandHandler("removelisting", remove_listing_command))
    app.add_handler(search_handler)
    app.add_handler(sell_handler)
    app.add_handler(browse_handler)

    print("Bot is running. Open Telegram and type /start to begin.")
    app.run_polling()
