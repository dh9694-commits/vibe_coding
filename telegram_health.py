import os
import time
from datetime import datetime
import requests
from dotenv import load_dotenv

load_dotenv()

BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN", "")

if not BOT_TOKEN:
    raise EnvironmentError("TELEGRAM_BOT_TOKEN 을 .env 에 설정하세요.")

BASE_URL = f"https://api.telegram.org/bot{BOT_TOKEN}"


def get_updates(offset=None) -> list:
    params = {"timeout": 30}
    if offset is not None:
        params["offset"] = offset
    res = requests.get(f"{BASE_URL}/getUpdates", params=params, timeout=35)
    res.raise_for_status()
    return res.json().get("result", [])


def send_reply(chat_id: int, text: str):
    requests.post(f"{BASE_URL}/sendMessage", json={
        "chat_id": chat_id,
        "text": text,
        "parse_mode": "HTML",
    }, timeout=10)


def main():
    print("🏥 헬스체크 봇 시작... (봇에 아무 메시지나 보내면 응답합니다)\n")
    offset = None
    while True:
        try:
            updates = get_updates(offset)
            for update in updates:
                offset = update["update_id"] + 1
                message = update.get("message", {})
                chat_id = message.get("chat", {}).get("id")
                if chat_id:
                    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                    send_reply(chat_id, f"✅ <b>정상 작동 중</b>\n🕐 {now}")
                    print(f"[헬스체크 응답] chat_id={chat_id} | {now}")
        except requests.RequestException as e:
            print(f"[오류] {e}")
            time.sleep(5)


if __name__ == "__main__":
    main()
