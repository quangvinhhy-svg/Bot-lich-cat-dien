import os
import requests
from bs4 import BeautifulSoup
import re

def boc_tach_cum_thong_tin(url_bai_viet, tu_khoa_muc_tieu):
    """Truy cập bài viết và lấy dữ liệu chi tiết (Điện lực + Ngày + Thời gian + Khu vực + Lý do + Trạng thái)"""
    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'}
    try:
        res = requests.get(url_bai_viet, headers=headers, timeout=25)
        res.encoding = 'utf-8'
        soup = BeautifulSoup(res.text, 'html.parser')
        
        # Tìm nội dung bài viết
        content = soup.find(['div', 'article'], class_=['entry-content', 'post-content'])
        if not content: 
            content = soup.body
        
        # Tách văn bản thành danh sách các dòng sạch
        lines = [l.strip() for l in content.get_text(separator="\n").split("\n") if l.strip()]
        text = "\n".join(lines)
        ket_qua = []

        # Regex tìm cụm thông tin
        pattern = re.compile(
            r"Điện lực.*?(?P<dien_luc>.+?)\s+"
            r"Ngày.*?(?P<ngay>.+?)\s+"
            r"Thời gian.*?(?P<thoi_gian>.+?)\s+"
            r"Khu vực.*?(?P<khu_vuc>.+?)\s+"
            r"Lý do.*?(?P<ly_do>.+?)\s+"
            r"Trạng thái.*?(?P<trang_thai>.+)",
            re.DOTALL
        )

        for match in pattern.finditer(text):
            dien_luc = match.group("dien_luc").strip()
            ngay = match.group("ngay").strip()
            thoi_gian = match.group("thoi_gian").strip()
            khu_vuc = match.group("khu_vuc").strip()
            ly_do = match.group("ly_do").strip()
            trang_thai = match.group("trang_thai").strip()

            # Chỉ lấy nếu khớp từ khóa mục tiêu
            if any(kv.lower() in dien_luc.lower() for kv in tu_khoa_muc_tieu):
                info_text = (
                    f"⚡ Điện lực: {dien_luc}\n"
                    f"📅 Ngày: {ngay}\n"
                    f"⏰ Thời gian: {thoi_gian}\n"
                    f"📍 Khu vực: {khu_vuc}\n"
                    f"🔧 Lý do: {ly_do}\n"
                    f"✅ Trạng thái: {trang_thai}"
                )
                ket_qua.append(info_text)

        return "\n\n".join(ket_qua)
    except Exception as e:
        return f"Lỗi khi xử lý: {e}"

def bat_dau_chay():
    token = os.environ.get('TELEGRAM_TOKEN')
    chat_id = os.environ.get('TELEGRAM_CHAT_ID')
    url_chinh = 'https://lichcupdien.org/lich-cup-dien-hung-yen'
    
    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'}
    # Danh sách đơn vị cần tìm
    don_vi_can_tim = ["Phù Tiên", "Kim Động", "Thành phố Hưng Yên"]
    
    try:
        response = requests.get(url_chinh, headers=headers, timeout=20)
        response.encoding = 'utf-8'
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # Quét 3 bài viết mới nhất trên trang chủ
        posts = soup.find_all('h3')[:3]
        found_data = False

        for post in posts:
            a_tag = post.find('a')
            if not a_tag: 
                continue
            
            link = a_tag['href']
            if not link.startswith('http'): 
                link = "https://lichcupdien.org" + link
            
            # Gọi hàm bóc tách dữ liệu chi tiết
            noi_dung = boc_tach_cum_thong_tin(link, don_vi_can_tim)
            
            if noi_dung:
                msg = f"⚡️ *CHI TIẾT LỊCH CẮT ĐIỆN* ⚡️\n📅 *{post.text.strip()}*\n\n{noi_dung}\n\n🔗 [Link gốc]({link})"
                requests.post(
                    f"https://api.telegram.org/bot{token}/sendMessage", 
                    json={"chat_id": chat_id, "text": msg, "parse_mode": "Markdown"}
                )
                found_data = True

        if not found_data:
            requests.post(
                f"https://api.telegram.org/bot{token}/sendMessage", 
                json={"chat_id": chat_id, "text": "✅ Hiện tại không tìm thấy dữ liệu chi tiết cho khu vực bạn yêu cầu."}
            )

    except Exception as e:
        print(f"Lỗi: {e}")

if __name__ == "__main__":
    bat_dau_chay()
