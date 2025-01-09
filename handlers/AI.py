from telegram import Update
from telegram.ext import ContextTypes
import google.generativeai as genai
from telegram.constants import ParseMode
import os
from config import reset_user_data
from dotenv import load_dotenv
from scholarly import scholarly
from services.crossref_service import fetch_article_by_doi
load_dotenv()
import re



gen_token =os.getenv("genai")

genai.configure(api_key=gen_token)
model = genai.GenerativeModel("gemini-1.5-flash")
import re





# async def summarizing(update:Update,context:ContextTypes.DEFAULT_TYPE):
#     article = update.message.text

#     reset_user_data(context)

#     try:
#         response = model.generate_content(f"""
# مقاله زیر رو بررسی کن و یک خلاصه خیلی کامل ازش بفرست واسم.
# خلاصه‌ای که مینویسی به زبان عامیانه و روان فارسی باشه.

# اگر مقاله واست در دسترس هم نیست . 
# فقط یک پیام کوتاه بنویس
# مثل مقاله در دسترس نیست یا openaccess نیست دوست عزیز.\n\n{str(article)}""")
            
#         await update.message.reply_text(response.text,parse_mode=ParseMode.MARKDOWN)
#     except Exception as e:
#         await context.bot.send_message(text=e,chat_id=1717599240)


async def summarizing(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_message = update.message.text.strip()
    user_id = update.effective_user.id

    try:
        await update.message.reply_text("⏳ در حال دریافت اطلاعات مقاله، لطفاً صبر کنید...")

        article_info = await fetch_article_by_doi(user_message)

        if article_info == "متاسفم، مقاله‌ای با این DOI پیدا نشد.":
            await update.message.reply_text("❌ مقاله‌ای با این DOI یافت نشد. لطفاً دوباره تلاش کنید.")
            return

        await update.message.reply_text("📄 در حال  خلاصه سازی . . .")
        summary = generate_summary(article_info)

        await update.message.reply_text(summary,parse_mode=ParseMode.MARKDOWN_V2)

    except ValueError as ve:
        print(f"User {user_id} encountered error: {str(ve)}")
        await update.message.reply_text(f"❌ {str(ve)}")

    except Exception as e:
        print(f"Unexpected error for user {user_id}: {str(e)}")
        await update.message.reply_text("❌ یک خطای غیرمنتظره رخ داده است. لطفاً دوباره تلاش کنید.")




def generate_summary(article_info):
    print(f"AI IS RUNNING > > > ")
    try:
        response = model.generate_content(f"""

مقاله زیر رو بررسی کن و یک خلاصه خیلی کامل ازش بفرست واسم.
خلاصه‌ای که مینویسی به زبان عامیانه و روان فارسی باشه.

{article_info}
        """)
        return str(response.text)
    except Exception as e:
        print(f"Error in generate_summary: {str(e)}")
        raise ValueError("خطایی در خلاصه‌سازی مقاله رخ داد.")


