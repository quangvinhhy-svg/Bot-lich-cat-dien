import os
import requests
from bs4 import BeautifulSoup

def lay_chi_tiet_tu_bang(url, khu_vuc_muc_tieu):
    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'}
    try:
        res = requests.get(url, headers=headers, timeout=20)
        res.encoding = 'utf-8'
        soup = BeautifulSoup(res.text, 'html.parser')
        
        # Tìm tất cả các bảng thông tin
        tables = soup.find_all('table')
        ket_qua = []
        
        for table in tables:
            rows = table.find_all('tr')
            for row in rows:
                text = row.get_text(separator=" ").strip()
                # Kiểm tra nếu dòng chứa từ khóa khu vực (ví dụ: Phù Tiên)
                if any(kv.lower() in text.lower() for kv in khu_vuc_muc_tieu):
                    # Làm sạch dữ liệu
                    clean_text = " ".join(text.split())
                    ket_qua.append(f"🔹 {clean_text}")
        
        return "\n\n".join(ket_qua)
    except:
        return ""

def bat_dau_chay():
    token = os.environ.get('TELEGRAM_TOKEN')
    chat_id = os.environ.get('TELEGRAM_CHAT_ID')
    url_chinh = 'https://lichcupdien.org/lich-cup-dien-hung-yen'
    
    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'}
    khu_vuc_loc = ["Phù Tiên", "Kim Động", "Thành phố Hưng Yên"]
    
    try:
        response = requests.get(url_chinh, headers=headers, timeout=20)
        response.encoding = 'utf-8'
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # Tìm các link bài viết (thường nằm trong thẻ h3)
        posts = soup.find_all('h3')
        found_any = False

        for post in posts[:3]:
            link_tag = post.find('a')
            if not link_tag: continue
            
            title = post.text.strip()
            link = link_tag['href']
            if not link.startswith('http'):
                link = "https://lichcupdien.org" + link
                
            # Truy cập sâu vào để lấy nội dung bảng
            chi_tiet = lay_chi_tiet_tu_bang(link, khu_vuc_loc)
            
            if chi_tiet:
                msg = f"⚡️ *LỊCH CẮT ĐIỆN CHI TIẾT* ⚡️\n📌 *{title}*\n\n{chi_tiet}\n\n🔗 [Link gốc]({link})"
                requests.post(f"https://api.telegram.org/bot{token}/sendMessage", 
                              json={"chat_id": chat_id, "text": msg, "parse_mode": "Markdown"})
                found_data = True
                found_any = True

        if not found_any:
            requests.post(f"https://api.telegram.org/bot{token}/sendMessage", 
                          json={"chat_id": chat_id, "text": "✅ Hiện tại không tìm thấy lịch cho Phù Tiên, Kim Động, TP Hưng Yên."})

    except Exception as e:
        print(f"Lỗi hệ thống: {e}")

if __name__ == "__main__":
    bat_dau_chay()
