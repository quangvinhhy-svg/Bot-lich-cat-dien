import os
import requests
from bs4 import BeautifulSoup

def bat_dau_chay():
    token = os.environ.get('TELEGRAM_TOKEN')
    chat_id = os.environ.get('TELEGRAM_CHAT_ID')
    url_chinh = 'https://lichcupdien.org/lich-cup-dien-hung-yen'
    
    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'}
    khu_vuc_loc = ["hưng yên", "tiên lữ", "kim động"]
    
    try:
        # 1. Lấy danh sách các bài thông báo mới nhất
        response = requests.get(url_chinh, headers=headers, timeout=20)
        response.encoding = 'utf-8'
        soup = BeautifulSoup(response.text, 'html.parser')
        items = soup.find_all(['div', 'article'], class_=['list-item', 'post-item']) or soup.find_all('h3')

        thong_bao_tong_hop = []

        for item in items[:3]: # Lấy tối đa 3 thông báo mới nhất để tránh tin nhắn quá dài
            title_tag = item.find('h3') if item.name != 'h3' else item
            if not title_tag: continue
            
            title_text = title_tag.text.strip()
            link_tag = item.find('a') if item.name != 'h3' else item.find_parent('a') or item.find('a')
            
            # Kiểm tra xem có thuộc khu vực quan tâm không
            if any(kv in title_text.lower() for kv in khu_vuc_loc) and link_tag:
                link_chi_tiet = link_tag['href']
                
                # 2. Truy cập vào link chi tiết để lấy nội dung bên trong
                res_detail = requests.get(link_chi_tiet, headers=headers, timeout=20)
                res_detail.encoding = 'utf-8'
                soup_detail = BeautifulSoup(res_detail.text, 'html.parser')
                
                # Tìm bảng hoặc khu vực chứa thông tin chi tiết
                content = soup_detail.find('div', class_='entry-content') or soup_detail.find('article')
                
                info_text = ""
                if content:
                    # Lấy các dòng thông tin như: Thời gian, Khu vực, Lý do
                    lines = content.find_all(['p', 'li'])
                    for line in lines:
                        txt = line.text.strip()
                        if any(key in txt for key in ["Thời gian:", "Khu vực:", "Lý do:", "Ngày:"]):
                            info_text += f"🔹 {txt}\n"
                
                detail_msg = f"📌 *{title_text}*\n{info_text if info_text else '⚠️ Không trích xuất được chi tiết, vui lòng xem link.'}\n🔗 [Xem chi tiết tại đây]({link_chi_tiet})"
                thong_bao_tong_hop.append(detail_msg)

        # 3. Gửi tin nhắn
        if thong_bao_tong_hop:
            final_msg = "⚡️ *CHI TIẾT LỊCH CẮT ĐIỆN HƯNG YÊN* ⚡️\n\n" + "\n\n---\n\n".join(thong_bao_tong_hop)
            requests.post(f"https://api.telegram.org/bot{token}/sendMessage", 
                          json={"chat_id": chat_id, "text": final_msg, "parse_mode": "Markdown", "disable_web_page_preview": True})
        else:
            requests.post(f"https://api.telegram.org/bot{token}/sendMessage", 
                          json={"chat_id": chat_id, "text": "✅ Hiện tại không có lịch cắt điện mới chi tiết cho khu vực của bạn."})

    except Exception as e:
        print(f"Lỗi: {e}")

if __name__ == "__main__":
    bat_dau_chay()

