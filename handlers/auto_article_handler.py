from telegram import Bot,Update
from telegram.ext import ContextTypes
from database import get_connection
from services.crossref_service import search_articles_by_keywords
import os

# TOKEN = os.getenv('TOKEN')
TOKEN ="7821187888:AAFCIAOfgZ6b9Jf7fOPI5Us0suzavuskXkg"
async def auto_article_task():
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute('SELECT chat_id, keywords FROM auto_article')
    user_keywords = cursor.fetchall()
    conn.close()

    bot = Bot(TOKEN)

    for chat_id, keywords in user_keywords:
        articles = await search_articles_by_keywords(keywords)
        if articles:
            message = f"📚 مقالات جدید مرتبط با کلمات کلیدی '{keywords}':\n\n"
            for article in articles:
                message += f"🔸 {article['title']}\n👨‍🔬 نویسنده: {article['author']}\n🔗 لینک: {article['url']}\n\n"
            await bot.send_message(chat_id=chat_id, text=message)
        else:
            await bot.send_message(chat_id=chat_id, text=f"مقاله‌ای مرتبط با '{keywords}' یافت نشد.")



async def manage_auto_article_sending(update:Update,context:ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(" این بخش فعلا در حال توسعه است ")