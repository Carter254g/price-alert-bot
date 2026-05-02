import os
import time
from dotenv import load_dotenv
from apscheduler.schedulers.blocking import BlockingScheduler
from src.checker import check_all
from src.telegram import send_message

load_dotenv()

def start_scheduler():
    interval_hours = int(os.getenv("CHECK_INTERVAL_HOURS", 6))

    send_message(f"Price Alert Bot started. Checking every {interval_hours} hour(s).")

    scheduler = BlockingScheduler()

    scheduler.add_job(
        check_all,
        "interval",
        hours=interval_hours,
        id="price_check",
    )

    print(f"Scheduler started. Checking every {interval_hours} hour(s).")
    print("Press Ctrl+C to stop.")

    check_all()

    try:
        scheduler.start()
    except KeyboardInterrupt:
        print("Scheduler stopped.")
        send_message("Price Alert Bot stopped.")
