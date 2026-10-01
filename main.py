import os
import re
import requests
from bs4 import BeautifulSoup

# 설정 정보
TARGET_URL = "https://bourse.operadeparis.fr/selection/event/date?productId=10229120931474&gtmStepTracking=true"
TARGET_DATES = ["18.10.2026", "19.10.2026"]

TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")  # 텔레그램 봇 토큰
TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")  # 사용자 Chat ID

HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/120.0.0.0 Safari/537.36"
    )
}


def send_telegram_msg(message):
    if not TELEGRAM_TOKEN or not TELEGRAM_CHAT_ID:
        print("텔레그램 토큰 또는 Chat ID가 설정되지 않았습니다.")
        print(message)
        return

    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
    payload = {
        "chat_id": TELEGRAM_CHAT_ID,
        "text": message,
        "parse_mode": "Markdown",
    }
    requests.post(url, data=payload)


def check_tickets():
    try:
        response = requests.get(TARGET_URL, headers=HEADERS, timeout=10)
        soup = BeautifulSoup(response.text, "html.parser")
        text_content = soup.get_text()

        found_tickets = []

        for date in TARGET_DATES:
            # 해당 날짜 주변 텍스트 검색
            pattern = re.compile(rf"{date}.*?(\d+)\s*tickets?", re.DOTALL)
            match = pattern.search(text_content)

            if match:
                ticket_count = int(match.group(1))
                if ticket_count > 0:
                    found_tickets.append(f"🎫 **{date}**: {ticket_count}장 오픈!")

        if found_tickets:
            alert_msg = (
                "🚨 **파리 오페라 극장 티켓 알림** 🚨\n\n"
                + "\n".join(found_tickets)
                + f"\n\n👉 [티켓 예매하러 가기]({TARGET_URL})"
            )
            send_telegram_msg(alert_msg)
            print("티켓 오픈 알림 전송 완료!")
        else:
            print("지정한 날짜에 이용 가능한 티켓이 없습니다.")

    except Exception as e:
        print(f"오류 발생: {e}")


if __name__ == "__main__":
    check_tickets()
