import requests
from bs4 import BeautifulSoup

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
}

def get_page(url):
    try:
        response = requests.get(url, headers=HEADERS, timeout=10)
        response.raise_for_status()
        return response.text
    except requests.RequestException as e:
        print(f"Error fetching {url}: {e}")
        return None

def extract_price(html):
    if not html:
        return None

    soup = BeautifulSoup(html, "lxml")

    selectors = [
        ("p", "price_color"),
        ("span", "price"),
        ("span", "amount"),
        ("div", "price"),
        ("p", "price"),
        ("span", "a-price-whole"),
        ("span", "woocommerce-Price-amount"),
    ]

    for tag, cls in selectors:
        element = soup.find(tag, class_=cls)
        if element:
            return clean_price(element.get_text())

    meta = soup.find("meta", itemprop="price")
    if meta:
        return clean_price(meta.get("content"))

    return None

def clean_price(price_text):
    if not price_text:
        return None
    cleaned = ""
    for char in price_text:
        if char.isdigit() or char == ".":
            cleaned += char
    if cleaned:
        try:
            return float(cleaned)
        except ValueError:
            return None
    return None

def extract_title(html):
    if not html:
        return "Unknown Product"
    soup = BeautifulSoup(html, "lxml")
    title = soup.find("title")
    if title:
        return title.get_text().strip()[:80]
    h1 = soup.find("h1")
    if h1:
        return h1.get_text().strip()[:80]
    return "Unknown Product"

def scrape(url):
    print(f"Scraping: {url}")
    html = get_page(url)
    if not html:
        return None

    price = extract_price(html)
    title = extract_title(html)

    result = {
        "url": url,
        "title": title,
        "price": price,
    }

    print(f"Title: {title}")
    print(f"Price: {price}")

    return result
