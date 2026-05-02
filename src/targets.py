import json
import os

TARGETS_FILE = "config/targets.json"

def load_targets():
    if not os.path.exists(TARGETS_FILE):
        return []
    with open(TARGETS_FILE, "r") as f:
        data = json.load(f)
        return data.get("targets", [])

def save_targets(targets):
    with open(TARGETS_FILE, "w") as f:
        json.dump({"targets": targets}, f, indent=2)

def add_target(url, target_price, label=""):
    targets = load_targets()
    for t in targets:
        if t["url"] == url:
            print(f"URL already being monitored: {url}")
            return False
    targets.append({
        "url": url,
        "target_price": target_price,
        "label": label or url,
        "last_price": None,
        "active": True
    })
    save_targets(targets)
    print(f"Added: {label or url} with target price {target_price}")
    return True

def remove_target(url):
    targets = load_targets()
    updated = [t for t in targets if t["url"] != url]
    if len(updated) == len(targets):
        print(f"URL not found: {url}")
        return False
    save_targets(updated)
    print(f"Removed: {url}")
    return True

def pause_target(url):
    targets = load_targets()
    for t in targets:
        if t["url"] == url:
            t["active"] = False
            save_targets(targets)
            print(f"Paused: {url}")
            return True
    print(f"URL not found: {url}")
    return False

def resume_target(url):
    targets = load_targets()
    for t in targets:
        if t["url"] == url:
            t["active"] = True
            save_targets(targets)
            print(f"Resumed: {url}")
            return True
    print(f"URL not found: {url}")
    return False

def update_last_price(url, price):
    targets = load_targets()
    for t in targets:
        if t["url"] == url:
            t["last_price"] = price
    save_targets(targets)
