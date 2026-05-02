from src.scraper import scrape
from src.telegram import send_price_alert, send_message
from src.targets import load_targets, update_last_price

def check_all():
    targets = load_targets()

    if not targets:
        print("No targets to check. Add one with: python bot.py add")
        return

    active_targets = [t for t in targets if t.get("active", True)]
    print(f"Checking {len(active_targets)} active target(s)...")

    alerts_sent = 0
    errors = 0
    no_price = 0

    for target in active_targets:
        url = target["url"]
        target_price = target["target_price"]
        label = target.get("label", url)

        result = scrape(url)

        if not result:
            print(f"Could not scrape: {url}")
            errors += 1
            continue

        current_price = result["price"]
        title = result["title"]

        if current_price is None:
            print(f"Could not extract price from: {url}")
            no_price += 1
            continue

        update_last_price(url, current_price)

        print(f"Checking: {label}")
        print(f"Current price: {current_price} | Target: {target_price}")

        if current_price <= target_price:
            print(f"Alert triggered for: {label}")
            send_price_alert(
                title=title,
                url=url,
                current_price=current_price,
                target_price=target_price
            )
            alerts_sent += 1
        else:
            diff = current_price - target_price
            print(f"No alert — price is {diff:.2f} above target")

    print(f"\nSummary: {alerts_sent} alert(s) sent, {errors} error(s), {no_price} price(s) not found.")

    if alerts_sent == 0 and errors == 0 and no_price == 0:
        print("All prices checked. No targets hit yet.")
