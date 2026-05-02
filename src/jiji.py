import requests
import json
import re

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
}

def scrape_jiji(query, min_price=None, max_price=None):
    try:
        url = f"https://jiji.co.ke/search?query={query.replace(' ', '+')}"
        if min_price:
            url += f"&price_min={int(min_price)}"
        if max_price:
            url += f"&price_max={int(max_price)}"

        res = requests.get(url, headers=HEADERS, timeout=10)

        match = re.search(r'id="__NUXT_DATA__"[^>]*>(.*?)</script>', res.text, re.DOTALL)
        if not match:
            return []

        data = json.loads(match.group(1))

        listings = []
        i = 0
        while i < len(data):
            item = data[i]
            if isinstance(item, dict) and "title" in item and "price_obj" in item:
                try:
                    title_idx = item.get("title")
                    price_idx = item.get("price_obj")
                    url_idx = item.get("url")
                    region_idx = item.get("region_name")

                    title = data[title_idx] if isinstance(title_idx, int) and title_idx < len(data) else None
                    url_path = data[url_idx] if isinstance(url_idx, int) and url_idx < len(data) else None
                    region = data[region_idx] if isinstance(region_idx, int) and region_idx < len(data) else ""

                    price = None
                    if isinstance(price_idx, int) and price_idx < len(data):
                        price_obj = data[price_idx]
                        if isinstance(price_obj, dict):
                            price_val_idx = price_obj.get("price")
                            if isinstance(price_val_idx, int) and price_val_idx < len(data):
                                price = data[price_val_idx]

                    if title and isinstance(title, str) and len(title) > 3:
                        if min_price and price and price < min_price:
                            i += 1
                            continue
                        if max_price and price and price > max_price:
                            i += 1
                            continue

                        full_url = f"https://jiji.co.ke{url_path}" if url_path and isinstance(url_path, str) and url_path.startswith("/") else ""
                        listings.append({
                            "title": title[:70],
                            "price": f"KES {price:,.0f}" if price else "Negotiable",
                            "raw_price": price,
                            "region": region if isinstance(region, str) else "",
                            "url": full_url,
                            "source": "Jiji Kenya",
                        })

                    if len(listings) >= 8:
                        break
                except Exception:
                    pass
            i += 1

        return listings

    except Exception as e:
        print(f"Jiji scrape error: {e}")
        return []
