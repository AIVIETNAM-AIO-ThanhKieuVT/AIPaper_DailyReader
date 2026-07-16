import os
import discord
from discord.ext import commands
from ai_core import fetch_latest_paper, summarize_paper, format_paper_message

# Lấy các biến môi trường
DISCORD_BOT_TOKEN = os.getenv("DISCORD_BOT_TOKEN")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

# Cấu hình quyền hạn của Bot
intents = discord.Intents.default()
intents.message_content = True  # Cho phép Bot đọc được nội dung tin nhắn

# Khởi tạo Bot với tiền tố (prefix) là "!"
bot = commands.Bot(command_prefix='!', intents=intents)

@bot.event
async def on_ready():
    print(f'✅ Bot {bot.user} đã thức dậy và sẵn sàng nhận lệnh!')
    print('Hãy Tag @Bot và gõ chủ đề báo bạn muốn đọc!')

@bot.event
async def on_message(message):
    # Bỏ qua tin nhắn do chính con Bot gửi
    if message.author == bot.user:
        return

    # Kiểm tra xem có ai Tag tên con Bot không
    if bot.user in message.mentions:
        # Xóa cái Tag (ví dụ: @AI_Paper_Bot) ra khỏi câu nói để lấy đúng cái Chủ đề
        topic = message.content.replace(f'<@{bot.user.id}>', '').strip()
        
        # Nếu Tag mà không nói gì
        if not topic:
            await message.channel.send("⚠️ Chị vừa gọi em nhưng chưa nhập chủ đề. Chị thử gõ: `@AI_Paper_Bot Computer Vision` nhé!")
            return
            
        msg = await message.channel.send(f"⏳ Đang lùng sục bài báo mới nhất về **{topic}** và nhờ AI tóm tắt. Chị đợi xíu nhé...")
        
        try:
            # 1. Tìm báo
            paper = fetch_latest_paper(topic)
            if not paper:
                await msg.edit(content=f"❌ Rất tiếc, em không tìm thấy bài báo nào về chủ đề **{topic}**.")
                return
                
            # 2. Tóm tắt
            summary = summarize_paper(paper, OPENAI_API_KEY)
            
            # 3. Format tin nhắn
            content = format_paper_message(paper, summary, topic)
            
            # 4. Gửi kết quả
            await msg.edit(content=content)
            
        except Exception as e:
            await msg.edit(content=f"❌ Đã xảy ra lỗi hệ thống: {str(e)}")

if __name__ == "__main__":
    if DISCORD_BOT_TOKEN:
        bot.run(DISCORD_BOT_TOKEN)
    else:
        print("❌ LỖI: Chưa cấu hình DISCORD_BOT_TOKEN.")
        print("Bạn cần tạo Token từ trang Discord Developer Portal và cấu hình biến môi trường.")
