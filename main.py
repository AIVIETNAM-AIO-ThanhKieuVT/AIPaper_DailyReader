import os
import arxiv
import requests
from openai import OpenAI
import datetime

# --- CONFIGURATION ---
# Môi trường CI/CD (GitHub Actions) sẽ tự động truyền 2 biến này vào
DISCORD_WEBHOOK_URL = os.getenv("DISCORD_WEBHOOK_URL")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

def get_topics():
    # Nhận Topic từ việc chạy thủ công trên GitHub (workflow_dispatch)
    manual_topic = os.getenv("MANUAL_TOPIC")
    if manual_topic:
        print(f"Sử dụng Topic chạy thủ công: {manual_topic}")
        return [manual_topic]
    
    # Nếu chạy tự động mỗi sáng (Cron), đọc từ file topics.txt
    try:
        with open("topics.txt", "r", encoding="utf-8") as f:
            topics = [line.strip() for line in f if line.strip()]
            print(f"Sử dụng Topic từ file cấu hình: {topics}")
            return topics
    except FileNotFoundError:
        print("Không tìm thấy file topics.txt, dùng mặc định.")
        return ["Generative AI"]

def fetch_latest_paper(topic):
    print(f"Đang tìm bài báo mới nhất về: {topic}")
    client = arxiv.Client()
    search = arxiv.Search(
        query=topic,
        max_results=1,
        sort_by=arxiv.SortCriterion.SubmittedDate
    )
    
    try:
        paper = next(client.results(search))
        return paper
    except StopIteration:
        return None

def summarize_paper(paper):
    print(f"Đang nhờ AI tóm tắt bài: {paper.title}...")
    if not OPENAI_API_KEY:
        return "⚠️ Lỗi: Chưa cấu hình OPENAI_API_KEY."

    client = OpenAI(api_key=OPENAI_API_KEY)
    
    prompt = f"""
    Bạn là một trợ lý AI đọc báo khoa học. Hãy đọc tiêu đề và tóm tắt (abstract) của bài báo sau đây và viết ra ĐÚNG 3 gạch đầu dòng (bullet points) bằng TIẾNG VIỆT để tóm tắt những ý chính quan trọng nhất.

    Tiêu đề: {paper.title}
    Tóm tắt gốc: {paper.summary}
    """
    
    try:
        response = client.chat.completions.create(
            model="gpt-3.5-turbo", # Có thể thay bằng gpt-4o tùy tài khoản
            messages=[
                {"role": "system", "content": "Bạn là chuyên gia dịch thuật và tóm tắt báo khoa học AI."},
                {"role": "user", "content": prompt}
            ],
            max_tokens=300
        )
        return response.choices[0].message.content
    except Exception as e:
        return f"⚠️ Lỗi khi gọi OpenAI API: {str(e)}"

def send_discord_message(title, authors, pdf_url, summary, topic):
    if not DISCORD_WEBHOOK_URL:
        print("⚠️ Bỏ qua gửi tin nhắn vì chưa cấu hình DISCORD_WEBHOOK_URL.")
        return

    content = f"""
📰 **BÁO CÁO AI HẰNG NGÀY - Chủ đề: {topic}**
*{datetime.datetime.now().strftime('%d/%m/%Y')}*

**{title}**
👨‍🔬 Tác giả: {authors}
🔗 Link PDF: {pdf_url}

**📌 Tóm tắt:**
{summary}
"""
    data = {"content": content}
    response = requests.post(DISCORD_WEBHOOK_URL, json=data)
    
    if response.status_code == 204:
        print("✅ Đã gửi báo cáo thành công lên Discord!")
    else:
        print(f"❌ Lỗi gửi tin nhắn Discord: {response.status_code} - {response.text}")

def main():
    topics = get_topics()
    for topic in topics:
        paper = fetch_latest_paper(topic)
        if paper:
            # Lấy tên tối đa 3 tác giả
            authors = ", ".join([author.name for author in paper.authors][:3])
            if len(paper.authors) > 3:
                authors += " và cộng sự"
            
            # Gọi LLM tóm tắt
            summary = summarize_paper(paper)
            
            # Gửi qua Discord
            send_discord_message(paper.title, authors, paper.pdf_url, summary, topic)
        else:
            print(f"Không tìm thấy bài báo nào cho chủ đề: {topic}")

if __name__ == "__main__":
    main()
