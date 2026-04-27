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


def is_real_delisting(title):
    title = title.lower()

    good_words = [
        "delist",
        "delisting",
        "remove",
        "removed",
        "trading pair delisting",
        "spot delisting",
        "notice regarding the early delisting",
        "delisting information",
        "token delisting"
    ]

    bad_words = [
        "futures",
        "perpetual",
        "maintenance",
        "margin",
        "launchpool",
        "campaign",
        "promo",
        "bonus",
        "earn",
        "apr",
        "staking",
        "reward"
    ]

    if any(word in title for word in bad_words):
        return False

    return any(word in title for word in good_words)


def check_bybit():
    url = "https://api.bybit.com/v5/announcements/index"

    params = {
        "locale": "en-US",
        "type": "delistings",
        "page": 1,
        "limit": 10
    }

    results = []

    try:
        r = requests.get(url, params=params, timeout=30)
        data = r.json()

        if "result" not in data:
            return results

        items = data["result"].get("list", [])

        for item in items:
            title = item.get("title", "")
            link = item.get("url", "")

            if not title:
                continue

            if is_real_delisting(title):
                results.append(("BYBIT", title, link))

    except Exception as e:
        print("BYBIT ERROR:", e)

    return results[:10]


def check_bitget():
    url = "https://api.bitget.com/api/v2/public/annoucements"

    params = {
        "language": "en_US",
        "annType": "symbol_delisting",
        "limit": "10"
    }

    results = []

    try:
        r = requests.get(url, params=params, timeout=30)
        data = r.json()

        if data.get("code") != "00000":
            return results

        items = data.get("data", [])

        for item in items:
            title = item.get("annTitle", "")
            link = item.get("annUrl", "")

            if not title:
                continue

            if is_real_delisting(title):
                results.append(("BITGET", title, link))

    except Exception as e:
        print("BITGET ERROR:", e)

    return results[:10]


def check_binance():
    url = "https://www.binance.com/en/support/announcement/list/161"

    results = []

    try:
        r = requests.get(url, timeout=30)
        soup = BeautifulSoup(r.text, "html.parser")

        for a in soup.find_all("a", href=True):
            title = a.get_text(strip=True)
            link = a["href"]

            if len(title) < 10:
                continue

            if is_real_delisting(title):
                if not link.startswith("http"):
                    link = "https://www.binance.com" + link

                results.append(("BINANCE", title, link))

    except Exception as e:
        print("BINANCE ERROR:", e)

    return results[:10]


def main():
    sent = load_sent()

    all_news = []
    all_news.extend(check_binance())
    all_news.extend(check_bybit())
    all_news.extend(check_bitget())

    print(all_news)

    for exchange, title, link in all_news:
        unique_id = f"{exchange}_{title}"

        if unique_id in sent:
            continue

        message = f"""
🚨 {exchange} DELISTING ALERT

{title}

{link}
"""

        send_telegram_message(message)
        sent.add(unique_id)

    save_sent(sent)


if __name__ == "__main__":
    main()


