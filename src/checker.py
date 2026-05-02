from src.scraper import scrape
from src.telegram import send_price_alert, send_message
from src.targets import load_targets, update_last_price

def check_all():
    targets = load_targets()

    if not targets:
        print("No targets to check. Add one with: python bot.py add")
        return

    print(f"Checking {len(targets)} target(s)...")

    for target in targets:
        if not target.get("active", True):
            continue

        url = target["url"]
        target_price = target["target_price"]
        label = target.get("label", url)

        result = scrape(url)

        if not result:
            print(f"Could not scrape: {url}")
            continue

        current_price = result["price"]
        title = result["title"]

        if current_price is None:
            print(f"Could not extract price from: {url}")
            continue

        update_last_price(url, current_price)

        print(f"Checking: {label}")
        print(f"Current price: {current_price} | Target: {target_price}")

        if current_price <= target_price:
            print(f"Price alert triggered for: {label}")
            send_price_alert(
                title=title,
                url=url,
                current_price=current_price,
                target_price=target_price
            )
        else:
            print(f"No alert — price {current_price} is above target {target_price}")

    print("Check complete.")
