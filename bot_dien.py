import os
import requests
from bs4 import BeautifulSoup

def lay_chi_tiet_lich(url):
    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'}
    try:
        res = requests.get(url, headers=headers, timeout=20)
        res.encoding = 'utf-8'
        soup = BeautifulSoup(res.text, 'html.parser')
        
        # Tìm phần nội dung chính của bài viết
        content = soup.find(['div', 'article'], class_=['entry-content', 'post-content'])
        if not content: return "Không tìm thấy nội dung chi tiết."

        lines = []
        # Quét qua các thẻ chứa chữ để nhặt thông tin
        for tag in content.find_all(['p', 'div', 'li']):
            text = tag.get_text(separator=" ").strip()
            # Chỉ lấy các dòng chứa từ khóa quan trọng
            if any(key in text for key in ["Thời gian:", "Khu vực:", "Lý do:", "Điện lực:"]):
                # Tránh lấy trùng lặp các dòng
                if text not in lines:
                    lines.append(f"🔹 {text}")
        
        return "\n".join(lines) if lines else "Lịch đã được đăng nhưng chưa có định dạng chi tiết cụ thể."
    except:
        return "Lỗi khi truy cập trang chi tiết."

def bat_dau_chay():
    token = os.environ.get('TELEGRAM_TOKEN')
    chat_id = os.environ.get('TELEGRAM_CHAT_ID')
    url_chinh = 'https://lichcupdien.org/lich-cup-dien-hung-yen'
    
    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'}
    khu_vuc_loc = ["hưng yên", "tiên lữ", "kim động"]
    
    try:
        response = requests.get(url_chinh, headers=headers, timeout=20)
        response.encoding = 'utf-8'
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # Tìm danh sách bài viết ở trang chủ
        posts = soup.find_all('h3')
        
        thong_bao_final = []

        for post in posts:
            title = post.text.strip()
            link_tag = post.find('a')
            if not link_tag: continue
            link = link_tag['href']

            # Kiểm tra xem bài viết có chứa khu vực bạn cần không
            if any(kv in title.lower() for kv in khu_vuc_loc):
                chi_tiet = lay_chi_tiet_lich(link)
                msg = f"📍 *{title}*\n{chi_tiet}\n🔗 [Xem hình ảnh gốc]({link})"
                thong_bao_final.append(msg)
            
            if len(thong_bao_final) >= 3: break # Lấy 3 ngày gần nhất

        if thong_bao_final:
            full_msg = "⚡️ *CHI TIẾT LỊCH CẮT ĐIỆN MỚI NHẤT* ⚡️\n\n" + "\n\n---\n\n".join(thong_bao_final)
            requests.post(f"https://api.telegram.org/bot{token}/sendMessage", 
                          json={"chat_id": chat_id, "text": full_msg, "parse_mode": "Markdown", "disable_web_page_preview": True})
        else:
            requests.post(f"https://api.telegram.org/bot{token}/sendMessage", 
                          json={"chat_id": chat_id, "text": "✅ Hiện tại không có lịch mới cho Hưng Yên, Tiên Lữ, Kim Động trên trang chủ."})

    except Exception as e:
        print(f"Lỗi hệ thống: {e}")

if __name__ == "__main__":
    bat_dau_chay()

