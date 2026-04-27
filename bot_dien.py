import os
import requests
from bs4 import BeautifulSoup

def lay_chi_tiet_lich(url, khu_vuc_quantam):
    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'}
    try:
        res = requests.get(url, headers=headers, timeout=20)
        res.encoding = 'utf-8'
        soup = BeautifulSoup(res.text, 'html.parser')
        
        # Tìm tất cả các bảng hoặc khối nội dung chi tiết
        content = soup.find(['div', 'article'], class_=['entry-content', 'post-content'])
        if not content: return ""

        # Tìm các khối lịch cụ thể (thường nằm trong thẻ div hoặc table)
        segments = content.find_all(['div', 'table', 'p'])
        
        ket_qua_chi_tiet = []
        current_info = ""
        
        for seg in segments:
            text = seg.get_text(separator=" ").strip()
            # Nếu dòng này chứa tên khu vực bạn cần
            if any(kv in text.lower() for kv in khu_vuc_quantam):
                # Thu thập thông tin xung quanh đó (Thời gian, Lý do...)
                current_info = f"📍 {text}\n"
                # Thử tìm các dòng lân cận để lấy thêm thời gian/lý do
                parent = seg.parent
                all_text = parent.get_text(separator="\n")
                ket_qua_chi_tiet.append(all_text)
                break # Tìm thấy khu vực đầu tiên khớp là lấy luôn

        return "\n".join(ket_qua_chi_tiet[:1]) # Tránh quá dài
    except:
        return ""

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
        
        posts = soup.find_all('h3')
        found_any = False

        for post in posts[:3]: # Kiểm tra 3 tin mới nhất
            title = post.text.strip()
            link_tag = post.find('a')
            if link_tag:
                link = link_tag['href']
                # Vào trang chi tiết để bóc tách dữ liệu cụ thể
                chi_tiet = lay_chi_tiet_lich(link, khu_vuc_loc)
                
                if chi_tiet:
                    msg = f"⚡️ *THÔNG BÁO CHI TIẾT* ⚡️\n\n{chi_tiet}\n\n🔗 [Xem ảnh gốc]({link})"
                    requests.post(f"https://api.telegram.org/bot{token}/sendMessage", 
                                  json={"chat_id": chat_id, "text": msg, "parse_mode": "Markdown"})
                    found_any = True

        if not found_any:
            requests.post(f"https://api.telegram.org/bot{token}/sendMessage", 
                          json={"chat_id": chat_id, "text": "✅ Không tìm thấy lịch chi tiết khớp với khu vực yêu cầu hôm nay."})

    except Exception as e:
        print(f"Lỗi: {e}")

if __name__ == "__main__":
    bat_dau_chay()
