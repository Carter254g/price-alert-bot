import json
import os
from datetime import datetime

LISTINGS_FILE = "config/listings.json"

def load_listings():
    if not os.path.exists(LISTINGS_FILE):
        return []
    with open(LISTINGS_FILE, "r") as f:
        data = json.load(f)
        return data.get("listings", [])

def save_listings(listings):
    with open(LISTINGS_FILE, "w") as f:
        json.dump({"listings": listings}, f, indent=2)

def add_listing(user_id, username, title, price, condition, description, photo_id=None):
    listings = load_listings()
    listing = {
        "id": len(listings) + 1,
        "user_id": user_id,
        "username": username or "unknown",
        "title": title,
        "price": price,
        "condition": condition,
        "description": description,
        "photo_id": photo_id,
        "active": True,
        "created_at": datetime.now().strftime("%Y-%m-%d %H:%M"),
    }
    listings.append(listing)
    save_listings(listings)
    return listing

def search_listings(query):
    listings = load_listings()
    query = query.lower()
    results = [
        l for l in listings
        if l.get("active", True) and (
            query in l["title"].lower() or
            query in l.get("description", "").lower()
        )
    ]
    return results

def get_my_listings(user_id):
    listings = load_listings()
    return [l for l in listings if l["user_id"] == user_id]

def remove_listing(user_id, listing_id):
    listings = load_listings()
    for l in listings:
        if l["id"] == listing_id and l["user_id"] == user_id:
            l["active"] = False
            save_listings(listings)
            return True
    return False
