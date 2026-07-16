import os
import requests
from ai_core import fetch_latest_paper, summarize_paper, format_paper_message

# Khai báo Webhook cho hệ thống báo thức lúc 7h sáng
DISCORD_WEBHOOK_URL = os.getenv("DISCORD_WEBHOOK_URL")

def get_topics():
    manual_topic = os.getenv("MANUAL_TOPIC")
    if manual_topic:
        return [manual_topic]
    
    try:
        with open("topics.txt", "r", encoding="utf-8") as f:
            return [line.strip() for line in f if line.strip()]
    except FileNotFoundError:
        return ["Generative AI"]

def main():
    topics = get_topics()
    for topic in topics:
        paper = fetch_latest_paper(topic)
        if paper:
            # Nhờ AI_Core tóm tắt và format tin nhắn
            summary = summarize_paper(paper)
            content = format_paper_message(paper, summary, topic)
            
            # Bắn tin nhắn qua Webhook
            if DISCORD_WEBHOOK_URL:
                data = {"content": content}
                response = requests.post(DISCORD_WEBHOOK_URL, json=data)
                if response.status_code == 204:
                    print("✅ Đã gửi báo cáo tự động thành công lên Discord!")
                else:
                    print(f"❌ Lỗi gửi tin nhắn: {response.status_code} - {response.text}")
            else:
                print("⚠️ Bỏ qua gửi tin nhắn vì chưa cấu hình DISCORD_WEBHOOK_URL.")
                print(content)
        else:
            print(f"Không tìm thấy bài báo nào cho chủ đề: {topic}")

if __name__ == "__main__":
    main()
