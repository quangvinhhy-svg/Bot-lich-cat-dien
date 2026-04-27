import os
import requests
from bs4 import BeautifulSoup

def lay_noi_dung_bang_chi_tiet(url_bai_viet, danh_sach_don_vi):
    """Truy cập link chi tiết bài viết và bóc tách dữ liệu từ bảng."""
    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'}
    try:
        res = requests.get(url_bai_viet, headers=headers, timeout=25)
        res.encoding = 'utf-8'
        soup = BeautifulSoup(res.text, 'html.parser')
        
        # Tìm tất cả các bảng dữ liệu trong bài viết
        tables = soup.find_all('table')
        if not tables:
            return ""

        dong_du_lieu = []
        for table in tables:
            rows = table.find_all('tr')
            for row in rows:
                text = row.get_text(separator=" ").strip()
                # Lọc chính xác theo tên các đơn vị điện lực yêu cầu
                if any(dv.lower() in text.lower() for dv in danh_sach_don_vi):
                    # Làm sạch văn bản (xóa khoảng trắng thừa)
                    clean_text = " ".join(text.split())
                    dong_du_lieu.append(f"🔹 {clean_text}")
        
        return "\n\n".join(dong_du_lieu)
    except Exception:
        return ""

def bat_dau_chay():
    token = os.environ.get('TELEGRAM_TOKEN')
    chat_id = os.environ.get('TELEGRAM_CHAT_ID')
    url_chinh = 'https://lichcupdien.org/lich-cup-dien-hung-yen'
    
    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'}
    # Danh sách đơn vị điện lực mục tiêu
    don_vi_muc_tieu = ["Phù Tiên", "Kim Động", "Thành phố Hưng Yên"]
    
    try:
        response = requests.get(url_chinh, headers=headers, timeout=20)
        response.encoding = 'utf-8'
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # Lấy danh sách tiêu đề bài viết (thường trong thẻ h3)
        posts = soup.find_all('h3')
        found_data = False

        for post in posts[:3]: # Kiểm tra 3 ngày gần nhất
            link_tag = post.find('a')
            if not link_tag: continue
            
            title = post.text.strip()
            link = link_tag['href']
            if not link.startswith('http'):
                link = "https://lichcupdien.org" + link

            # Bước quan trọng: Đi sâu vào trong link để lấy bảng chi tiết
            chi_tiet = lay_noi_dung_bang_chi_tiet(link, don_vi_muc_tieu)
            
            if chi_tiet:
                msg = f"⚡️ *LỊCH CẮT ĐIỆN CHI TIẾT* ⚡️\n📅 *{title}*\n\n{chi_tiet}\n\n🔗 [Xem ảnh gốc]({link})"
                requests.post(f"https://api.telegram.org/bot{token}/sendMessage", 
                              json={"chat_id": chat_id, "text": msg, "parse_mode": "Markdown"})
                found_data = True

        if not found_data:
            msg_fail = "✅ Hiện tại trang chủ không có thông tin chi tiết cho: Phù Tiên, Kim Động, TP Hưng Yên."
            requests.post(f"https://api.telegram.org/bot{token}/sendMessage", 
                          json={"chat_id": chat_id, "text": msg_fail})

    except Exception as e:
        print(f"Lỗi: {e}")

if __name__ == "__main__":
    bat_dau_chay()
