import os
import arxiv
from openai import OpenAI

def fetch_latest_paper(topic):
    print(f"Đang tìm bài báo mới nhất về: {topic}")
    client = arxiv.Client()
    search = arxiv.Search(
        query=topic,
        max_results=1,
        sort_by=arxiv.SortCriterion.SubmittedDate
    )
    try:
        return next(client.results(search))
    except StopIteration:
        return None

def summarize_paper(paper, openai_api_key=None):
    if not openai_api_key:
        openai_api_key = os.getenv("OPENAI_API_KEY")
        
    if not openai_api_key:
        return "⚠️ Lỗi: Chưa cấu hình OPENAI_API_KEY."

    print(f"Đang nhờ AI tóm tắt: {paper.title}...")
    client = OpenAI(api_key=openai_api_key)
    
    prompt = f"""
    Bạn là một trợ lý AI đọc báo khoa học. Hãy đọc tiêu đề và tóm tắt (abstract) của bài báo sau đây và viết ra ĐÚNG 3 gạch đầu dòng (bullet points) bằng TIẾNG VIỆT để tóm tắt những ý chính quan trọng nhất, dễ hiểu nhất.

    Tiêu đề: {paper.title}
    Tóm tắt gốc: {paper.summary}
    """
    
    try:
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "Bạn là chuyên gia dịch thuật và tóm tắt báo khoa học AI."},
                {"role": "user", "content": prompt}
            ],
            max_tokens=300
        )
        return response.choices[0].message.content
    except Exception as e:
        return f"⚠️ Lỗi khi gọi OpenAI API: {str(e)}"

def format_paper_message(paper, summary, topic):
    authors = ", ".join([author.name for author in paper.authors][:3])
    if len(paper.authors) > 3:
        authors += " và cộng sự"
        
    import datetime
    date_str = datetime.datetime.now().strftime('%d/%m/%Y')
        
    return f"""📰 **BÁO CÁO AI - Chủ đề: {topic}**
*{date_str}*

**{paper.title}**
👨‍🔬 Tác giả: {authors}
🔗 Link PDF: {paper.pdf_url}

**📌 Tóm tắt:**
{summary}
"""
