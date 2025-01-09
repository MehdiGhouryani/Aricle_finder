from telegram import Update
from telegram.ext import ContextTypes
import google.generativeai as genai
from telegram.constants import ParseMode
import os
from config import reset_user_data
from dotenv import load_dotenv

load_dotenv()



gen_token =os.getenv("genai")

genai.configure(api_key=gen_token)
model = genai.GenerativeModel("gemini-1.5-flash")

async def summarizing(update:Update,context:ContextTypes.DEFAULT_TYPE):
    article = update.message.text

    reset_user_data(context)

    try:
        response = model.generate_content(f"""
مقاله زیر رو بررسی کن و یک خلاصه خیلی کامل ازش بفرست واسم.
خلاصه‌ای که مینویسی به زبان عامیانه و روان فارسی باشه.

اگر مقاله واست در دسترس هم نیست . 
فقط یک پیام کوتاه بنویس
مثل مقاله در دسترس نیست یا openaccess نیست دوست عزیز.\n\n{str(article)}""")
            
        await update.message.reply_text(response.text,parse_mode=ParseMode.MARKDOWN)
    except Exception as e:
        await context.bot.send_message(text=e,chat_id=1717599240)
