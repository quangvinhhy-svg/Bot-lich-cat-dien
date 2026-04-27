import os
import requests
from bs4 import BeautifulSoup

def bat_dau_chay():
    # 1. Cấu hình thông tin
    token = os.environ.get('TELEGRAM_TOKEN')
    chat_id = os.environ.get('TELEGRAM_CHAT_ID')
    url = 'https://lichcupdien.org/lich-cup-dien-hung-yen'
    
    # Gửi tin nhắn thử nghiệm để chắc chắn kết nối Telegram đã thông
    requests.post(f"https://api.telegram.org/bot{token}/sendMessage", 
                  json={"chat_id": chat_id, "text": "🤖 Bot Hưng Yên đang kiểm tra lịch cắt điện..."})

    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'}
    khu_vuc = ["Thành phố Hưng Yên", "Tiên Lữ", "Kim Động"]
    
    try:
        response = requests.get(url, headers=headers)
        response.encoding = 'utf-8'
        soup = BeautifulSoup(response.text, 'html.parser')
        items = soup.find_all('div', class_='list-item')
        
        ket_qua = []
        for item in items:
            title = item.find('h3').text.strip()
            link = item.find('a')['href']
            if any(kv.lower() in title.lower() for kv in khu_vuc):
                ket_qua.append(f"📍 {title}\n🔗 Chi tiết: {link}")
            
            if len(ket_qua) >= 5:
                break

        if not ket_qua:
            msg = "✅ Hiện tại không có lịch cắt điện mới cho TP. Hưng Yên, Tiên Lữ, Kim Động."
        else:
            msg = "⚡️ THÔNG BÁO LỊCH CẮT ĐIỆN ⚡️\n\n" + "\n------------------------\n".join(ket_qua)
        
        # Gửi kết quả cuối cùng
        requests.post(f"https://api.telegram.org/bot{token}/sendMessage", 
                      json={"chat_id": chat_id, "text": msg, "disable_web_page_preview": True})
        print("Đã chạy xong!")

    except Exception as e:
        print(f"Lỗi: {e}")

if __name__ == "__main__":
    bat_dau_chay()

