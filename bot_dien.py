import os
import requests
from bs4 import BeautifulSoup

def bat_dau_chay():
    token = os.environ.get('TELEGRAM_TOKEN')
    chat_id = os.environ.get('TELEGRAM_CHAT_ID')
    url = 'https://lichcupdien.org/lich-cup-dien-hung-yen'
    
    # Giả lập trình duyệt để không bị trang web chặn
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
    }
    
    # Danh sách từ khóa ngắn gọn để tăng tỉ lệ tìm thấy
    khu_vuc = ["hưng yên", "tiên lữ", "kim động"]
    
    try:
        response = requests.get(url, headers=headers, timeout=20)
        response.encoding = 'utf-8'
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # Tìm tất cả các tiêu đề bản tin (thường nằm trong thẻ h3 hoặc class list-item)
        items = soup.find_all(['div', 'article'], class_=['list-item', 'post-item']) 
        if not items:
            # Nếu không tìm thấy class, thử tìm theo tất cả các thẻ h3
            items = soup.find_all('h3')

        ket_qua = []
        for item in items:
            title_tag = item.find('h3') if item.name != 'h3' else item
            if title_tag:
                title = title_tag.text.strip()
                # Tìm link: nếu item không phải h3 thì tìm thẻ a bên trong, nếu là h3 thì tìm thẻ a chứa nó
                link_tag = item.find('a') if item.name != 'h3' else item.find_parent('a') or item.find('a')
                link = link_tag['href'] if link_tag else url
                
                # Kiểm tra khu vực (không phân biệt hoa thường)
                if any(kv in title.lower() for kv in khu_vuc):
                    ket_qua.append(f"📍 {title}\n🔗 Chi tiết: {link}")
            
            if len(ket_qua) >= 5: break

        if not ket_qua:
            msg = "✅ Hiện tại không có lịch cắt điện mới được đăng cho TP. Hưng Yên, Tiên Lữ, Kim Động trên trang chủ."
        else:
            msg = "⚡️ THÔNG BÁO LỊCH CẮT ĐIỆN ⚡️\n\n" + "\n------------------------\n".join(ket_qua)
        
        requests.post(f"https://api.telegram.org/bot{token}/sendMessage", 
                      json={"chat_id": chat_id, "text": msg, "disable_web_page_preview": True})

    except Exception as e:
        requests.post(f"https://api.telegram.org/bot{token}/sendMessage", 
                      json={"chat_id": chat_id, "text": f"❌ Lỗi kỹ thuật: {str(e)}"})

if __name__ == "__main__":
    bat_dau_chay()

