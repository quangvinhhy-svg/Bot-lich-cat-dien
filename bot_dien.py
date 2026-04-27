import os
import requests
from bs4 import BeautifulSoup

def bat_dau_chay():
    token = os.environ.get('TELEGRAM_TOKEN')
    chat_id = os.environ.get('TELEGRAM_CHAT_ID')
    url_chinh = 'https://lichcupdien.org/lich-cup-dien-hung-yen'
    
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
    }
    # Từ khóa quét linh hoạt hơn để không bỏ lỡ thông báo nào
    khu_vuc_loc = ["hưng yên", "tiên lữ", "kim động"]
    
    try:
        response = requests.get(url_chinh, headers=headers, timeout=25)
        response.encoding = 'utf-8'
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # Tìm tất cả các bài viết có thể chứa lịch
        items = soup.find_all(['h3', 'div', 'article'], class_=['list-item', 'post-item', 'entry-title'])
        if not items:
            items = soup.find_all('h3')

        thong_bao_tong_hop = []

        for item in items:
            title_tag = item.find('a') if item.name != 'a' else item
            if not title_tag:
                title_tag = item
            
            title_text = title_tag.text.strip()
            link_chi_tiet = title_tag.get('href') if title_tag.name == 'a' else (item.find('a').get('href') if item.find('a') else None)

            if link_chi_tiet and any(kv in title_text.lower() for kv in khu_vuc_loc):
                if not link_chi_tiet.startswith('http'):
                    link_chi_tiet = "https://lichcupdien.org" + link_chi_tiet
                
                # Truy cập sâu vào bài viết để lấy thông tin chi tiết
                res_detail = requests.get(link_chi_tiet, headers=headers, timeout=25)
                res_detail.encoding = 'utf-8'
                soup_detail = BeautifulSoup(res_detail.text, 'html.parser')
                
                # Quét diện rộng nội dung bài viết
                content_div = soup_detail.find(['div', 'article'], class_=['entry-content', 'post-content', 'content'])
                info_text = ""
                
                if content_div:
                    # Lấy tất cả văn bản trong các thẻ p, li, div con
                    elements = content_div.find_all(['p', 'li', 'div'])
                    for el in elements:
                        txt = el.text.strip()
                        # Lọc lấy các dòng chứa thông tin quan trọng
                        if any(key in txt for key in ["Thời gian:", "Khu vực:", "Lý do:", "Ngày:", "Đến:"]):
                            if txt not in info_text: # Tránh lặp lại nội dung
                                info_text += f"🔹 {txt}\n"
                
                detail_msg = f"📌 *{title_text}*\n{info_text if info_text else '⚠️ Không tự động trích xuất được chi tiết.'}\n🔗 [Mở trang chi tiết]({link_chi_tiet})"
                thong_bao_tong_hop.append(detail_msg)
            
            if len(thong_bao_tong_hop) >= 3: break

        if thong_bao_tong_hop:
            final_msg = "⚡️ *CHI TIẾT LỊCH CẮT ĐIỆN HƯNG YÊN* ⚡️\n\n" + "\n\n---\n\n".join(thong_bao_tong_hop)
            requests.post(f"https://api.telegram.org/bot{token}/sendMessage", 
                          json={"chat_id": chat_id, "text": final_msg, "parse_mode": "Markdown", "disable_web_page_preview": True})
        else:
            requests.post(f"https://api.telegram.org/bot{token}/sendMessage", 
                          json={"chat_id": chat_id, "text": "✅ Hiện tại trang chủ không hiển thị lịch mới cho các khu vực bạn yêu cầu."})

    except Exception as e:
        print(f"Lỗi: {e}")

if __name__ == "__main__":
    bat_dau_chay()

