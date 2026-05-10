# 텔레그램 키워드 알림 봇

특정 텔레그램 채팅방을 감시하다가 키워드가 포함된 메시지가 오면 내 텔레그램 봇으로 알림을 전달하는 프로그램.  
GCP e2-micro (무료 티어) 위에서 24/7 상시 실행.

## 파일 구조

| 파일 | 역할 |
|---|---|
| `telegram_watcher.py` | 메인 실행 파일. Telethon으로 채팅방 감시, 키워드 매칭, 알림 발송 |
| `telegram_notify.py` | 텔레그램 Bot API HTTP 래퍼. `send_message()` 등 알림 함수 모음 |
| `telegram_health.py` | 헬스체크 봇. 봇에 메시지 오면 정상 작동 여부 응답 |
| `.env` | 인증 정보 및 설정값 (Git 제외) |
| `watcher_session` | Telethon 로그인 세션 파일 (Git 제외) |

## 동작 방식

- **이벤트 기반** — 폴링 아님. Telegram 서버가 새 메시지를 push함 (`events.NewMessage`)
- **시작 시**: 감시 채팅방의 미읽음 메시지를 먼저 처리 후 실시간 모니터링 시작
- **메시지 분할**: Telegram Bot API 4096자 한도 초과 시 자동으로 여러 메시지로 분할 전송

## .env 설정값

```
TELEGRAM_API_ID       # my.telegram.org 에서 발급 (내 계정 API)
TELEGRAM_API_HASH     # my.telegram.org 에서 발급 (내 계정 API)
WATCH_CHAT            # 감시할 채팅방. 쉼표로 여러 개 가능 (username 또는 숫자 chat_id)
KEYWORDS              # 알림 받을 키워드 목록. 쉼표로 구분
TELEGRAM_BOT_TOKEN    # 알림 발송용 봇 토큰 (@BotFather 에서 발급)
TELEGRAM_CHAT_ID      # 알림 받을 채팅 ID (내 계정 또는 그룹)
```

## 실행 방법 (GCP)

```bash
# 최초 설치
git clone https://github.com/dh9694-commits/vibe_coding.git
cd vibe_coding
pip3 install telethon python-dotenv requests --break-system-packages
nano .env  # 환경변수 입력

# tmux로 백그라운드 실행
tmux new -s watcher
python3 telegram_watcher.py
# Ctrl+B → D 로 detach

# 헬스체크 봇 별도 실행
tmux new -s health
python3 telegram_health.py
# Ctrl+B → D 로 detach

# 코드 업데이트 시
git pull origin main
# tmux 세션에서 프로세스 재시작
```

## 개발 컨벤션

- 기능마다 브랜치 생성 후 작업 (`feature/기능명`)
- 완성 후 PR → main merge
- `.env`, `*.session` 은 절대 커밋 금지
- 알림 함수는 `telegram_notify.py`에 추가, 감시 로직은 `telegram_watcher.py`에 추가
