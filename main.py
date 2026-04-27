import requests
import os
import json
from bs4 import BeautifulSoup

BOT_TOKEN = os.getenv("BOT_TOKEN")
CHAT_ID = os.getenv("CHAT_ID")

SENT_FILE = "sent.json"


def load_sent():
    try:
        with open(SENT_FILE, "r", encoding="utf-8") as f:
            return set(json.load(f))
    except:
        return set()


def save_sent(data):
    with open(SENT_FILE, "w", encoding="utf-8") as f:
        json.dump(list(data), f)


def send_telegram_message(text):
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"

    response = requests.post(url, data={
        "chat_id": CHAT_ID,
        "text": text
    })

    print(response.text)


def is_delisting(title):
    keywords = [
        "delist",
        "delisting",
        "remove",
        "removed",
        "trading pairs will be removed",
        "spot trading will be suspended"
    ]

    title_lower = title.lower()
    return any(word in title_lower for word in keywords)


def check_binance():
    url = "https://www.binance.com/en/support/announcement/c-48"
    r = requests.get(url, timeout=20)
    soup = BeautifulSoup(r.text, "html.parser")

    results = []

    for a in soup.find_all("a", href=True):
        title = a.get_text(strip=True)
        link = a["href"]

        if len(title) < 10:
            continue

        if is_delisting(title):
            if not link.startswith("http"):
                link = "https://www.binance.com" + link

            results.append(("BINANCE", title, link))

    return results


def check_bybit():
    url = "https://announcements.bybit.com/en-US/"
    r = requests.get(url, timeout=20)
    soup = BeautifulSoup(r.text, "html.parser")

    results = []

    for a in soup.find_all("a", href=True):
        title = a.get_text(strip=True)
        link = a["href"]

        if len(title) < 10:
            continue

        if is_delisting(title):
            if not link.startswith("http"):
                link = "https://announcements.bybit.com" + link

            results.append(("BYBIT", title, link))

    return results


def check_bitget():
    url = "https://www.bitget.com/support/articles"
    r = requests.get(url, timeout=20)
    soup = BeautifulSoup(r.text, "html.parser")

    results = []

    for a in soup.find_all("a", href=True):
        title = a.get_text(strip=True)
        link = a["href"]

        if len(title) < 10:
            continue

        if is_delisting(title):
            if not link.startswith("http"):
                link = "https://www.bitget.com" + link

            results.append(("BITGET", title, link))

    return results


def main():
  
    sent = load_sent()

    all_news = []
    all_news.extend(check_binance())
    all_news.extend(check_bybit())
    all_news.extend(check_bitget())

    for exchange, title, link in all_news:
        unique_id = f"{exchange}_{title}"

        if unique_id in sent:
            continue

        message = f"""
{exchange} DELISTING ALERT

{title}

{link}
"""

        send_telegram_message(message)
        sent.add(unique_id)

    save_sent(sent)


if __name__ == "__main__":
    main()
