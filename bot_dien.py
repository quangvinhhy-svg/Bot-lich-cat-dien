import os
import requests
from bs4 import BeautifulSoup

def lay_thong_tin_chi_tiet(url_bai_viet, tu_khoa):
    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'}
    try:
        res = requests.get(url_bai_viet, headers=headers, timeout=20)
        res.encoding = 'utf-8'
        soup = BeautifulSoup(res.text, 'html.parser')
        
        # Quét toàn bộ nội dung văn bản của bài viết
        content = soup.find(['div', 'article'], class_=['entry-content', 'post-content', 'content'])
        if not content: content = soup.body
        
        lines = content.get_text(separator="\n").split("\n")
        ket_qua = []
        
        for i, line in enumerate(lines):
            text = line.strip()
            # Nếu tìm thấy tên điện lực yêu cầu
            if any(k.lower() in text.lower() for k in tu_khoa):
                # Lấy dòng đó và 5 dòng tiếp theo (thường chứa Giờ, Khu vực, Lý do)
                cum_info = " | ".join([l.strip() for l in lines[i:i+6] if l.strip()])
                ket_qua.append(f"🔹 {cum_info}")
        
        return "\n\n".join(list(dict.fromkeys(ket_qua))) # Xóa trùng lặp
    except:
        return ""

def bat_dau_chay():
    token = os.environ.get('TELEGRAM_TOKEN')
    chat_id = os.environ.get('TELEGRAM_CHAT_ID')
    url_tong = 'https://lichcupdien.org/lich-cup-dien-hung-yen'
    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'}
    don_vi = ["Phù Tiên", "Kim Động", "Thành phố Hưng Yên"]

    try:
        response = requests.get(url_tong, headers=headers, timeout=20)
        response.encoding = 'utf-8'
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # Tìm 3 bài viết mới nhất
        posts = soup.find_all('h3')[:3]
        found = False

        for post in posts:
            a_tag = post.find('a')
            if not a_tag: continue
            
            link = a_tag['href']
            if not link.startswith('http'): link = "https://lichcupdien.org" + link
            
            # ĐIỀU CHỈNH QUAN TRỌNG: Truy cập vào link chi tiết để lấy dữ liệu
            chi_tiet = lay_thong_tin_chi_tiet(link, don_vi)
            
            if chi_tiet:
                msg = f"⚡️ *LỊCH CẮT ĐIỆN CHI TIẾT* ⚡️\n📅 *{post.text.strip()}*\n\n{chi_tiet}\n\n🔗 [Xem gốc]({link})"
                requests.post(f"https://api.telegram.org/bot{token}/sendMessage", 
                              json={"chat_id": chat_id, "text": msg, "parse_mode": "Markdown"})
                found = True

        if not found:
            requests.post(f"https://api.telegram.org/bot{token}/sendMessage", 
                          json={"chat_id": chat_id, "text": "✅ Không tìm thấy lịch chi tiết cho Phù Tiên, Kim Động, TP Hưng Yên hôm nay."})
    except Exception as e:
        print(f"Lỗi: {e}")

if __name__ == "__main__":
    bat_dau_chay()
