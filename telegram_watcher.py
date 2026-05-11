import os
import sys
import asyncio
from pathlib import Path
from telethon import TelegramClient, events
from dotenv import load_dotenv
from telegram_notify import send_message
import telegram_health

# Windows 터미널 한글/이모지 출력 설정
sys.stdout = open(sys.stdout.fileno(), mode='w', encoding='utf-8', buffering=1)


load_dotenv()

# ── 내 계정 API 정보 (my.telegram.org 에서 발급) ──────────────────
API_ID   = int(os.getenv("TELEGRAM_API_ID", "0"))
API_HASH = os.getenv("TELEGRAM_API_HASH", "")

# ── 감시할 채팅방 (쉼표로 구분, username 또는 숫자 chat_id) ──────
# 예) WATCH_CHAT=channel_a,channel_b,-1001234567890
WATCH_CHATS = [
    c.strip()
    for c in os.getenv("WATCH_CHAT", "").split(",")
    if c.strip()
]

# ── 알림 받고 싶은 키워드 목록 ────────────────────────────────────
KEYWORDS = [
    kw.strip()
    for kw in os.getenv("KEYWORDS", "").split(",")
    if kw.strip()
]

# ─────────────────────────────────────────────────────────────────
if not API_ID or not API_HASH:
    raise EnvironmentError("TELEGRAM_API_ID 와 TELEGRAM_API_HASH 를 .env 에 설정하세요.")
if not WATCH_CHATS:
    raise EnvironmentError("WATCH_CHAT 을 .env 에 설정하세요.")
if not KEYWORDS:
    raise EnvironmentError("KEYWORDS 를 .env 에 설정하세요. (쉼표로 구분)")

print(f"✅ 감시 채팅방 : {WATCH_CHATS}")
print(f"✅ 키워드 목록 : {KEYWORDS}")

SESSION_FILE = str(Path(__file__).parent / "watcher_session")
client = TelegramClient(SESSION_FILE, API_ID, API_HASH)

TELEGRAM_LIMIT = 4096


def send_alert(header: str, msg_text: str) -> bool:
    """헤더 + 본문을 4096자 단위로 나눠서 전송"""
    footer = "\n────────────────────"
    first_limit = TELEGRAM_LIMIT - len(header) - len(footer)
    ok = send_message(header + msg_text[:first_limit] + footer)

    remaining = msg_text[first_limit:]
    part = 2
    while remaining:
        prefix = f"📄 <b>(이어서 {part})</b>\n"
        chunk_limit = TELEGRAM_LIMIT - len(prefix) - len(footer)
        chunk = remaining[:chunk_limit]
        remaining = remaining[chunk_limit:]
        suffix = footer if not remaining else ""
        send_message(f"{prefix}{chunk}{suffix}")
        part += 1

    return ok


async def process_unread():
    """스크립트 시작 시 모든 감시 채팅방의 미읽음 메시지를 키워드 검사 후 알림 발송"""
    watch_set = {c.lstrip('@') for c in WATCH_CHATS}

    async for dialog in client.iter_dialogs():
        entity = dialog.entity
        username = (getattr(entity, 'username', '') or '').lstrip('@')
        entity_id = str(getattr(entity, 'id', 0))

        if username not in watch_set and entity_id not in watch_set:
            continue

        unread_count = dialog.unread_count
        if unread_count == 0:
            print(f"📭 [{dialog.name}] 미읽음 없음")
            continue

        print(f"📬 [{dialog.name}] 미읽음 {unread_count}개 처리 중...")
        messages = await client.get_messages(entity, limit=unread_count)
        sent = 0
        for msg in reversed(messages):
            msg_text = msg.message or ""
            matched = [kw for kw in KEYWORDS if kw.lower() in msg_text.lower()]
            if matched:
                sender_name = "알 수 없음"
                if msg.sender_id:
                    try:
                        sender = await client.get_entity(msg.sender_id)
                        sender_name = getattr(sender, "username", None) or getattr(sender, "first_name", "알 수 없음")
                    except Exception:
                        pass
                header = (
                    f"🔔 <b>키워드 알림 (미읽음)</b>\n"
                    f"────────────────────\n"
                    f"📌 키워드 : <b>{', '.join(matched)}</b>\n"
                    f"👤 발신자 : {sender_name}\n"
                    f"💬 내용 :\n"
                )
                ok = send_alert(header, msg_text)
                print(f"[미읽음 알림 전송{'✅' if ok else '❌'}] 키워드={matched} | 발신={sender_name}")
                if ok:
                    sent += 1
        print(f"📬 [{dialog.name}] 미읽음 처리 완료 (알림 {sent}건 발송)")

    print()


@client.on(events.NewMessage(chats=WATCH_CHATS))
async def handler(event):
    msg_text = event.message.message or ""
    matched = [kw for kw in KEYWORDS if kw.lower() in msg_text.lower()]

    if matched:
        sender = await event.get_sender()
        sender_name = getattr(sender, "username", None) or getattr(sender, "first_name", "알 수 없음")

        header = (
            f"🔔 <b>키워드 알림</b>\n"
            f"────────────────────\n"
            f"📌 키워드 : <b>{', '.join(matched)}</b>\n"
            f"👤 발신자 : {sender_name}\n"
            f"💬 내용 :\n"
        )
        ok = send_alert(header, msg_text)
        print(f"[알림 전송{'✅' if ok else '❌'}] 키워드={matched} | 발신={sender_name}")


async def main():
    await client.start()
    print("👀 메시지 모니터링 시작...\n")
    await process_unread()
    asyncio.create_task(telegram_health.run())
    await client.run_until_disconnected()


client.loop.run_until_complete(main())
