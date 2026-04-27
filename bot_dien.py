import os
import requests
from bs4 import BeautifulSoup

# Danh sách điện lực cần lấy
DIEN_LUC_CAN_TIM = [
    "Điện Lực Phù Tiên",
    "Điện Lực Thành Phố Hưng Yên",
    "Điện Lực Kim Động"
]

URL_CHINH = "https://lichcupdien.org/lich-cup-dien-hung-yen"

def lay_thong_tin_dien_luc(url):
    """Truy cập bài viết và lấy thông tin chi tiết theo nhãn"""
    headers = {"User-Agent": "Mozilla/5.0"}
    res = requests.get(url, headers=headers, timeout=25)
    res.encoding = "utf-8"
    soup = BeautifulSoup(res.text, "html.parser")

    content = soup.find(["div","article"], class_=["entry-content","post-content"])
    if not content:
        content = soup.body

    lines = [l.strip() for l in content.get_text(separator="\n").split("\n") if l.strip()]

    ket_qua = []
    block = {}

    for line in lines:
        if line.startswith("Điện lực"):
            block = {"dien_luc": line.split(":",1)[1].strip()}
        elif line.startswith("Ngày"):
            block["ngay"] = line.split(":",1)[1].strip()
        elif line.startswith("Thời gian"):
            block["thoi_gian"] = line.split(":",1)[1].strip()
        elif line.startswith("Khu vực"):
            block["khu_vuc"] = line.split(":",1)[1].strip()
        elif line.startswith("Lý do"):
            block["ly_do"] = line.split(":",1)[1].strip()
        elif line.startswith("Trạng thái"):
            block["trang_thai"] = line.split(":",1)[1].strip()
            # Khi đủ thông tin thì kiểm tra xem có nằm trong danh sách cần tìm
            if any(dl.lower() in block["dien_luc"].lower() for dl in DIEN_LUC_CAN_TIM):
                ket_qua.append(
                    f"⚡ Điện lực: {block['dien_luc']}\n"
                    f"📅 Ngày: {block['ngay']}\n"
                    f"⏰ Thời gian: {block['thoi_gian']}\n"
                    f"📍 Khu vực: {block['khu_vuc']}\n"
                    f"🔧 Lý do: {block['ly_do']}\n"
                    f"✅ Trạng thái: {block['trang_thai']}"
                )
            block = {}

    return "\n\n".join(ket_qua)

def gui_thong_bao_telegram(noi_dung, tieu_de, link):
    token = os.environ.get("TELEGRAM_TOKEN")
    chat_id = os.environ.get("TELEGRAM_CHAT_ID")
    msg = f"⚡️ *CHI TIẾT LỊCH CẮT ĐIỆN* ⚡️\n📅 *{tieu_de}*\n\n{noi_dung}\n\n🔗 [Link gốc]({link})"
    requests.post(
        f"https://api.telegram.org/bot{token}/sendMessage",
        json={"chat_id": chat_id, "text": msg, "parse_mode": "Markdown"}
    )

def bat_dau_chay():
    headers = {"User-Agent": "Mozilla/5.0"}
    try:
        response = requests.get(URL_CHINH, headers=headers, timeout=20)
        response.encoding = "utf-8"
        soup = BeautifulSoup(response.text, "html.parser")

        posts = soup.find_all("h3")[:3]
        found_data = False

        for post in posts:
            a_tag = post.find("a")
            if not a_tag:
                continue

            link = a_tag["href"]
            if not link.startswith("http"):
                link = "https://lichcupdien.org" + link

            noi_dung = lay_thong_tin_dien_luc(link)
            if noi_dung:
                gui_thong_bao_telegram(noi_dung, post.text.strip(), link)
                found_data = True

        if not found_data:
            token = os.environ.get("TELEGRAM_TOKEN")
            chat_id = os.environ.get("TELEGRAM_CHAT_ID")
            requests.post(
                f"https://api.telegram.org/bot{token}/sendMessage",
                json={"chat_id": chat_id, "text": "✅ Hiện tại không tìm thấy dữ liệu chi tiết cho khu vực bạn yêu cầu."}
            )

    except Exception as e:
        print(f"Lỗi: {e}")

if __name__ == "__main__":
    bat_dau_chay()
