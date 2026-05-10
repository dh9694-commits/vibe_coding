import os
import asyncio
from datetime import datetime
import requests
from dotenv import load_dotenv

load_dotenv()

BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN", "")
BASE_URL = f"https://api.telegram.org/bot{BOT_TOKEN}"


def _get_updates(offset=None) -> list:
    params = {"timeout": 30}
    if offset is not None:
        params["offset"] = offset
    res = requests.get(f"{BASE_URL}/getUpdates", params=params, timeout=35)
    res.raise_for_status()
    return res.json().get("result", [])


def _send_reply(chat_id: int, text: str):
    requests.post(f"{BASE_URL}/sendMessage", json={
        "chat_id": chat_id,
        "text": text,
        "parse_mode": "HTML",
    }, timeout=10)


async def run():
    """watcher 와 함께 실행되는 헬스체크 루프"""
    print("🏥 헬스체크 대기 중... (봇에 아무 메시지나 보내면 응답)\n")
    offset = None
    while True:
        try:
            updates = await asyncio.to_thread(_get_updates, offset)
            for update in updates:
                offset = update["update_id"] + 1
                message = update.get("message", {})
                chat_id = message.get("chat", {}).get("id")
                if chat_id:
                    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                    await asyncio.to_thread(_send_reply, chat_id,
                        f"✅ <b>정상 작동 중</b>\n🕐 {now}")
                    print(f"[헬스체크 응답] {now}")
        except Exception as e:
            print(f"[헬스체크 오류] {e}")
            await asyncio.sleep(5)
