import os
import requests
from bs4 import BeautifulSoup

def lay_chi_tiet_lich(url, tu_khoa_loc):
    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'}
    try:
        res = requests.get(url, headers=headers, timeout=20)
        res.encoding = 'utf-8'
        soup = BeautifulSoup(res.text, 'html.parser')
        
        # Tìm tất cả các bảng dữ liệu chi tiết
        tables = soup.find_all('table')
        if not tables:
            return ""

        ket_qua_bang = []
        for table in tables:
            rows = table.find_all('tr')
            for row in rows:
                row_text = row.get_text(separator=" ").strip()
                # Chuyển về chữ thường để so sánh không phân biệt hoa thường
                if any(kv.lower() in row_text.lower() for kv in tu_khoa_loc):
                    # Làm sạch khoảng trắng thừa
                    clean_row = " ".join(row_text.split())
                    ket_qua_bang.append(f"🔹 {clean_row}")
        
        return "\n".join(ket_qua_bang)
    except:
        return ""

def bat_dau_chay():
    token = os.environ.get('TELEGRAM_TOKEN')
    chat_id = os.environ.get('TELEGRAM_CHAT_ID')
    url_chinh = 'https://lichcupdien.org/lich-cup-dien-hung-yen'
    
    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'}
    # Danh sách các đơn vị điện lực bạn quan tâm
    dien_luc_quan_tam = ["Phù Tiên", "Kim Động", "Thành phố Hưng Yên"]
    
    try:
        response = requests.get(url_chinh, headers=headers, timeout=20)
        response.encoding = 'utf-8'
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # Lấy danh sách các bài viết mới nhất (thẻ h3)
        posts = soup.find_all('h3')
        da_co_tin_nhan = False

        # Kiểm tra 3 bài viết mới nhất trên trang chủ
        for post in posts[:3]:
            link_tag = post.find('a')
            if not link_tag: continue
            
            title = post.text.strip()
            link_bai_viet = link_tag['href']
            if not link_bai_viet.startswith('http'):
                link_bai_viet = "https://lichcupdien.org" + link_bai_viet

            # Lấy thông tin chi tiết từ bảng bên trong bài viết
            noi_dung_chi_tiet = lay_chi_tiet_lich(link_bai_viet, dien_luc_quan_tam)
            
            if noi_dung_chi_tiet:
                msg = f"⚡️ *CHI TIẾT LỊCH CẮT ĐIỆN* ⚡️\n📅 *{title}*\n\n{noi_dung_chi_tiet}\n\n🔗 [Xem ảnh gốc]({link_bai_viet})"
                
                # Gửi tin nhắn về Telegram
                requests.post(f"https://api.telegram.org/bot{token}/sendMessage", 
                              json={"chat_id": chat_id, "text": msg, "parse_mode": "Markdown"})
                da_co_tin_nhan = True

        if not da_co_tin_nhan:
            requests.post(f"https://api.telegram.org/bot{token}/sendMessage", 
                          json={"chat_id": chat_id, "text": "✅ Hiện tại không thấy lịch cắt điện chi tiết cho Phù Tiên, Kim Động, TP Hưng Yên."})

    except Exception as e:
        print(f"Lỗi: {e}")

if __name__ == "__main__":
    bat_dau_chay()
