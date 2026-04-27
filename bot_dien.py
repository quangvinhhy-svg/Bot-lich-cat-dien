import requests
from bs4 import BeautifulSoup
import os
from datetime import datetime, timedelta
import re

# ===== CONFIG =====
URL = "https://lichcupdien.org/lich-cup-dien-hung-yen"

TELEGRAM_TOKEN = os.environ.get("TELEGRAM_TOKEN")
CHAT_ID = os.environ.get("TELEGRAM_CHAT_ID")

TARGETS = [
    "ĐIỆN LỰC PHÙ TIÊN",
    "ĐIỆN LỰC KIM ĐỘNG",
    "ĐIỆN LỰC THÀNH PHỐ HƯNG YÊN"
]

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


# ===== PARSE DATE =====
def parse_date(date_str):
    match = re.search(r"(\d+)\s+tháng\s+(\d+)\s+năm\s+(\d+)", date_str)
    if not match:
        return None

    day, month, year = map(int, match.groups())
    return datetime(year, month, day)


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

        if "Điện lực" in key:
            if current:
                data.append(current)
                current = {}

        current[key] = value

    if current:
        data.append(current)

    # ===== TIME (VN) =====
    now_vn = datetime.utcnow() + timedelta(hours=7)
    today = now_vn.date()
    tomorrow = today + timedelta(days=1)

    results = {target: [] for target in TARGETS}

    for item in data:
        power = item.get("Điện lực:", "")

        matched_target = None
        for target in TARGETS:
            if target in power:
                matched_target = target
                break

        if not matched_target:
            continue

        parsed_date = parse_date(item.get("Ngày:", ""))
        if not parsed_date:
            continue

        item_date = parsed_date.date()

        if item_date == today or item_date == tomorrow:
            # thêm flag để biết hôm nay hay mai
            item["__type"] = "today" if item_date == today else "tomorrow"
            results[matched_target].append(item)

    return results


# ===== FORMAT =====
def format_message(data_dict):
    now_vn = datetime.utcnow() + timedelta(hours=7)
    today = now_vn.date()
    tomorrow = today + timedelta(days=1)

    today_str = today.strftime("%d/%m")
    tomorrow_str = tomorrow.strftime("%d/%m")

    msg = "⚡ <b>LỊCH CẮT ĐIỆN</b>\n"
    msg += f"📅 <b>{today_str} (HÔM NAY)</b>\n"
    msg += f"📅 <b>{tomorrow_str} (NGÀY MAI)</b>\n\n"

    for target in TARGETS:
        items = data_dict.get(target, [])

        msg += f"🏢 <b>{target}</b>\n"

        if not items:
            msg += "❌ Không có lịch cắt điện.\n"
            msg += "----------------------\n"
            continue

        for item in items:
            label = "🔴 HÔM NAY" if item.get("__type") == "today" else "🟡 NGÀY MAI"

            msg += f"{label}\n"
            msg += f"⏰ {item.get('Thời gian:', '')}\n"
            msg += f"📍 {item.get('Khu vực:', '')}\n"
            msg += f"🛠 {item.get('Lý do:', '')}\n"
            msg += "----------------------\n"

    return msg


# ===== MAIN =====
def main():
    print("🚀 Đang chạy bot...")

    data = get_data()
    print("✅ Đã lấy dữ liệu")

    message = format_message(data)

    send_telegram(message)
    print("✅ Đã gửi Telegram")


if __name__ == "__main__":
    main()
