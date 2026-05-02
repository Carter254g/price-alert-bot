import os
from dotenv import load_dotenv
from serpapi import GoogleSearch

load_dotenv()

SERPAPI_KEY = os.getenv("SERPAPI_KEY")

COUNTRIES = {
    "1": {"name": "Kenya", "gl": "ke", "hl": "en", "currency": "KES"},
    "2": {"name": "USA", "gl": "us", "hl": "en", "currency": "USD"},
    "3": {"name": "UK", "gl": "gb", "hl": "en", "currency": "GBP"},
    "4": {"name": "Nigeria", "gl": "ng", "hl": "en", "currency": "NGN"},
    "5": {"name": "South Africa", "gl": "za", "hl": "en", "currency": "ZAR"},
    "6": {"name": "Uganda", "gl": "ug", "hl": "en", "currency": "UGX"},
    "7": {"name": "Tanzania", "gl": "tz", "hl": "en", "currency": "TZS"},
    "8": {"name": "Germany", "gl": "de", "hl": "en", "currency": "EUR"},
}

def get_countries_text():
    text = "Which country are you shopping in?\n\n"
    for key, country in COUNTRIES.items():
        text += f"{key}. {country['name']}\n"
    return text

def get_country(choice):
    return COUNTRIES.get(str(choice))

def search_products(query, country_code="us"):
    try:
        params = {
            "engine": "google",
            "q": f"{query} buy price",
            "api_key": SERPAPI_KEY,
            "num": 10,
            "gl": country_code,
            "hl": "en",
        }

        search = GoogleSearch(params)
        results = search.get_dict()

        organic_results = results.get("organic_results", [])
        inline_shopping = results.get("inline_shopping_results", [])

        products = []

        for item in inline_shopping[:5]:
            title = item.get("title", "Unknown")
            price = item.get("price", "No price")
            source = item.get("source", "Unknown store")
            link = item.get("link", "")
            products.append({
                "title": title[:60],
                "price": price,
                "raw_price": None,
                "source": source,
                "link": link,
            })

        for item in organic_results:
            if len(products) >= 8:
                break
            title = item.get("title", "Unknown")
            link = item.get("link", "")
            source = item.get("displayed_link", "")
            snippet = item.get("snippet", "")

            price = "Check site for price"
            import re
            price_match = re.search(r'(KES|Ksh|USD|\$|£|€|NGN|ZAR)\s?[\d,]+', snippet)
            if price_match:
                price = price_match.group()

            products.append({
                "title": title[:60],
                "price": price,
                "raw_price": None,
                "source": source,
                "link": link,
            })

        return products

    except Exception as e:
        print(f"Search error: {e}")
        return []
