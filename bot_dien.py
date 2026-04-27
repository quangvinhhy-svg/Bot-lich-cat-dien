
import requests
from bs4 import BeautifulSoup
import os

# ===== CONFIG =====
URL = "https://lichcupdien.org/lich-cup-dien-hung-yen"

TELEGRAM_TOKEN = os.environ.get("TELEGRAM_TOKEN")
CHAT_ID = os.environ.get("TELEGRAM_CHAT_ID")

TARGETS = [
    "ĐIỆN LỰC PHÙ TIÊN",
    "ĐIỆN LỰC KIM ĐỘNG",
    "ĐIỆN LỰC THÀNH PHỐ HƯNG YÊN"
]


# ===== CHECK ENV =====
if not TELEGRAM_TOKEN or not CHAT_ID:
    raise ValueError("Thiếu TELEGRAM_TOKEN hoặc TELEGRAM_CHAT_ID")


# ===== TELEGRAM =====
def send_telegram(message):
    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"

    res = requests.post(url, data={
        "chat_id": CHAT_ID,
        "text": message,
        "parse_mode": "HTML"
    })

    if res.status_code != 200:
        print("❌ Lỗi gửi Telegram:", res.text)


# ===== SCRAPE =====
def get_data():
    res = requests.get(URL)
    soup = BeautifulSoup(res.text, "html.parser")

    data = []
    current = {}

    items = soup.find_all("div", class_="new_lcd_wrapper")

    for item in items:
        title = item.find("span", class_="title_item_lcd_wrapper")
        content = item.find("span", class_="content_item_content_lcd_wrapper")

        if not title or not content:
            continue

        key = title.get_text(strip=True)
        value = content.get_text(" ", strip=True)

        # bắt đầu bản ghi mới khi gặp "Điện lực"
        if "Điện lực" in key:
            if current:
                data.append(current)
                current = {}

        current[key] = value

    if current:
        data.append(current)

    # ===== FILTER =====
    results = []
    for item in data:
        if any(target in item.get("Điện lực:", "") for target in TARGETS):
            results.append(item)

    return results


# ===== FORMAT =====
def format_message(data_list):
    if not data_list:
        return "❌ Không có lịch cắt điện phù hợp."

    msg = "⚡ <b>LỊCH CẮT ĐIỆN HƯNG YÊN</b>\n\n"

    for item in data_list:
        msg += f"🏢 <b>{item.get('Điện lực:', '')}</b>\n"
        msg += f"📅 {item.get('Ngày:', '')}\n"
        msg += f"⏰ {item.get('Thời gian:', '')}\n"
        msg += f"📍 {item.get('Khu vực:', '')}\n"
        msg += f"🛠 {item.get('Lý do:', '')}\n"
        msg += "----------------------\n"

    return msg


# ===== MAIN =====
def main():
    print("🚀 Đang chạy bot...")

    data = get_data()
    print(f"✅ Lấy được {len(data)} bản ghi")

    message = format_message(data)
    send_telegram(message)

    print("✅ Đã gửi Telegram")


if __name__ == "__main__":
    main()
