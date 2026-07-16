import os
import arxiv
import google.generativeai as genai

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

def summarize_paper(paper, api_key=None):
    # Lấy Key từ biến môi trường OPENAI_API_KEY (vì trên Render chị Kều đang đặt tên biến này)
    if not api_key:
        api_key = os.getenv("OPENAI_API_KEY")
        
    if not api_key:
        return "⚠️ Lỗi: Chưa cấu hình API_KEY."

    print(f"Đang nhờ Gemini AI tóm tắt: {paper.title}...")
    
    prompt = f"""
    Bạn là một trợ lý AI đọc báo khoa học. Hãy đọc tiêu đề và tóm tắt (abstract) của bài báo sau đây và viết ra ĐÚNG 3 gạch đầu dòng (bullet points) bằng TIẾNG VIỆT để tóm tắt những ý chính quan trọng nhất, dễ hiểu nhất.

    Tiêu đề: {paper.title}
    Tóm tắt gốc: {paper.summary}
    """
    
    try:
        genai.configure(api_key=api_key)
        # Sử dụng model nhanh và rẻ nhất của Google
        model = genai.GenerativeModel('gemini-1.5-flash')
        response = model.generate_content(prompt)
        return response.text
    except Exception as e:
        return f"⚠️ Lỗi khi gọi Google Gemini API: {str(e)}"

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
