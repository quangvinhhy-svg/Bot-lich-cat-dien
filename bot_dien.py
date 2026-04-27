import os  # Dòng này cực kỳ quan trọng, phải có nó mới chạy được
import requests
from bs4 import BeautifulSoup

# Cấu hình thông tin (Lấy từ Secrets của GitHub)
TOKEN = os.environ.get('TELEGRAM_TOKEN')
CHAT_ID = os.environ.get('TELEGRAM_CHAT_ID')
URL = 'https://lichcupdien.org/lich-cup-dien-hung-yen'

def get_power_cut_data():
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
    }
    
    khu_vuc_quantam = ["Thành phố Hưng Yên", "Tiên Lữ", "Kim Động"]
    
    try:
        response = requests.get(URL, headers=headers)
        response.encoding = 'utf-8' 
        soup = BeautifulSoup(response.text, 'html.parser')
        
        items = soup.find_all('div', class_='list-item')
        
        if not items:
            return "📭 Hiện tại không tìm thấy lịch cắt điện mới trên hệ thống."

        ket_qua = []
        for item in items:
            title = item.find('h3').text.strip()
            link = item.find('a')['href']
            
            if any(kv.lower() in title.lower() for kv in khu_vuc_quantam):
                ket_qua.append(f"📍 {title}\n🔗 Chi tiết: {link}")
            
            if len(ket_qua) >= 5:
                break

        if not ket_qua:
            return "✅ Hiện tại không có lịch cắt điện cho TP. Hưng Yên, Tiên Lữ, Kim Động."

        message = "⚡️ THÔNG BÁO LỊCH CẮT ĐIỆN ⚡️\n"
        message += "\n------------------------\n".join(ket_qua)
        return message

    except Exception as e:
        return f"❌ Có lỗi xảy ra khi lấy dữ liệu: {str(e)}"

def send_telegram(text):
    if not TOKEN or not CHAT_ID:
        print("Lỗi: Thiếu TOKEN hoặc CHAT_ID!")
        return
        
    send_url = f"https://api.telegram.org/bot{TOKEN}/sendMessage"
    payload = {
        "chat_id": CHAT_ID, 
        "text": text,
        "disable_web_page_preview": True 
    }
    requests.post(send_url, json=payload)

if __name__ == "__main__":
    content = get_power_cut_data()
    send_telegram(content)

