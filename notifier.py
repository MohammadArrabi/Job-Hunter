import os

import requests
from dotenv import load_dotenv

load_dotenv()

BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")


def _call_telegram(method, **kwargs):
    if not BOT_TOKEN or not CHAT_ID:
        print("Telegram is not configured: add TELEGRAM_BOT_TOKEN and TELEGRAM_CHAT_ID to .env")
        return False

    url = f"https://api.telegram.org/bot{BOT_TOKEN}/{method}"
    try:
        response = requests.post(url, timeout=30, **kwargs)
    except requests.RequestException as e:
        print(f"Telegram {method} failed: network error ({type(e).__name__})")
        return False

    if not response.ok:
        print(f"Telegram {method} failed: {response.status_code} {response.text}")
        return False

    print(f"Telegram {method} sent")
    return True


def send_message(text):
    return _call_telegram("sendMessage", data={"chat_id": CHAT_ID, "text": text})


def send_photo(photo_path, caption=""):
    with open(photo_path, "rb") as photo:
        return _call_telegram(
            "sendPhoto",
            data={"chat_id": CHAT_ID, "caption": caption},
            files={"photo": photo},
        )