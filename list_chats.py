import os
import asyncio
from pathlib import Path
from telethon import TelegramClient
from dotenv import load_dotenv

load_dotenv()

API_ID   = int(os.getenv("TELEGRAM_API_ID", "0"))
API_HASH = os.getenv("TELEGRAM_API_HASH", "")

async def list_chats():
    SESSION_FILE = str(Path(__file__).parent / "watcher_session")
    async with TelegramClient(SESSION_FILE, API_ID, API_HASH) as client:
        print("\n📋 내 텔레그램 채팅방 목록\n" + "="*50)
        async for dialog in client.iter_dialogs():
            entity = dialog.entity
            username = getattr(entity, "username", None)
            chat_id  = dialog.id
            name     = dialog.name

            if username:
                watch_value = username
            else:
                watch_value = str(chat_id)

            print(f"  이름  : {name}")
            print(f"  WATCH_CHAT 에 입력할 값 : {watch_value}")
            print("-" * 50)

asyncio.run(list_chats())
