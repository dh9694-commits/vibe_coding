import os
import requests
from datetime import datetime
from dotenv import load_dotenv

load_dotenv()

BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN", "")
CHAT_ID = os.getenv("TELEGRAM_CHAT_ID", "")

if not BOT_TOKEN or not CHAT_ID:
    raise EnvironmentError("TELEGRAM_BOT_TOKEN과 TELEGRAM_CHAT_ID를 .env 파일에 설정하세요.")

BASE_URL = f"https://api.telegram.org/bot{BOT_TOKEN}"


def send_message(text: str, parse_mode: str = "HTML") -> bool:
    url = f"{BASE_URL}/sendMessage"
    payload = {
        "chat_id": CHAT_ID,
        "text": text,
        "parse_mode": parse_mode,
    }
    try:
        res = requests.post(url, json=payload, timeout=10)
        res.raise_for_status()
        return True
    except requests.RequestException as e:
        print(f"[오류] 메시지 전송 실패: {e}")
        return False


def send_stock_alert(title: str, content: str, category: str = "일반") -> bool:
    now = datetime.now().strftime("%Y-%m-%d %H:%M")
    tag_map = {
        "매수": "🟢",
        "매도": "🔴",
        "리포트": "📄",
        "뉴스": "📰",
        "자동매매": "🤖",
        "경고": "⚠️",
        "일반": "📌",
    }
    icon = tag_map.get(category, "📌")
    text = (
        f"{icon} <b>[{category}] {title}</b>\n"
        f"────────────────────\n"
        f"{content}\n"
        f"────────────────────\n"
        f"🕐 {now}"
    )
    return send_message(text)


def send_trade_alert(stock_name: str, action: str, price: float, quantity: int, reason: str = "") -> bool:
    icon = "🟢 매수" if action == "buy" else "🔴 매도"
    text = (
        f"🤖 <b>자동매매 체결 알림</b>\n"
        f"────────────────────\n"
        f"종목: <b>{stock_name}</b>\n"
        f"구분: {icon}\n"
        f"가격: {price:,.0f}원\n"
        f"수량: {quantity}주\n"
        f"금액: {price * quantity:,.0f}원\n"
    )
    if reason:
        text += f"사유: {reason}\n"
    text += f"────────────────────\n🕐 {datetime.now().strftime('%Y-%m-%d %H:%M')}"
    return send_message(text)


if __name__ == "__main__":
    print("연결 테스트 중...")
    ok = send_message("✅ 텔레그램 알림 봇 연결 성공!\n앞으로 주식 알림을 이 채팅으로 받을 수 있어요.")
    if ok:
        print("전송 성공!")
    else:
        print("전송 실패 — 토큰 또는 Chat ID를 확인하세요.")
