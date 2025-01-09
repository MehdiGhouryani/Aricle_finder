from telegram import Update
from telegram.ext import ContextTypes
import google.generativeai as genai
from telegram.constants import ParseMode
import os
from config import reset_user_data
from dotenv import load_dotenv
from scholarly import scholarly
load_dotenv()


gen_token =os.getenv("genai")

genai.configure(api_key=gen_token)
model = genai.GenerativeModel("gemini-1.5-flash")


import re

def extract_doi_from_url(url):
    match = re.search(r'doi\.org/([0-9]+(?:\.[0-9]+)+)', url)
    if match:
        return match.group(1)
    else:
        return None


async def summarizing(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_input = update.message.text.strip()
    
    if 'doi.org' in user_input:
        doi = extract_doi_from_url(user_input)
        if not doi:
            await update.message.reply_text("لطفاً یک DOI معتبر وارد کنید.")
            return
    elif re.match(r'^\d{4}/\d{9}', user_input):  # DOI معمولی
        doi = user_input
    else:
        await update.message.reply_text("لطفاً DOI یا لینک معتبر مقاله را وارد کنید.")
        return    
    try:
        article = scholarly.search_pubs(doi)
        article_info = next(article)

        title = article_info['bib'].get('title', 'عنوان نامشخص')
        abstract = article_info['bib'].get('abstract', 'چکیده موجود نیست')
        authors = article_info['bib'].get('author', 'نویسندگان نامشخص')
        year = article_info['bib'].get('pub_year', 'سال نامشخص')

        prompt = f"""
        مقاله‌ای با عنوان "{title}" پیدا شده است. اطلاعات آن به صورت زیر است:
        
        چکیده: {abstract}
        نویسندگان: {authors}
        سال انتشار: {year}
        
        حالا این مقاله را به صورت کامل خلاصه کن و توضیح بده.
        """

        # ارسال اطلاعات به مدل هوش مصنوعی برای خلاصه‌سازی
        response = model.generate_content(prompt)
        
        # ارسال نتیجه به کاربر
        await update.message.reply_text(
            f"خلاصه مقاله {title}:\n\n{response.text}",
            parse_mode=ParseMode.MARKDOWN
        )
    except Exception as e:
        await update.message.reply_text("خطایی در دریافت اطلاعات مقاله رخ داد. لطفاً دوباره تلاش کنید.")



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


# async def summarizing(update: Update, context: ContextTypes.DEFAULT_TYPE):
#     user_message = update.message.text.strip()
#     user_id = update.effective_user.id

#     try:
#         await update.message.reply_text("⏳ در حال دریافت اطلاعات مقاله، لطفاً صبر کنید...")

#         article_info = fetch_info(user_message)

#         await update.message.reply_text(
#             f"📄 اطلاعات مقاله دریافت شد:\n\n"
#             f"**عنوان:** {article_info['title']}\n"
#             f"**نویسنده(ها):** {article_info['authors']}\n"
#             f"🔄 در حال آماده‌سازی خلاصه مقاله...",
#             parse_mode=ParseMode.MARKDOWN
#         )

#         summary = generate_summary(article_info)

#         await update.message.reply_text(summary, parse_mode=ParseMode.MARKDOWN)

#     except ValueError as ve:
#         print(f"User {user_id} encountered error: {str(ve)}")
#         await update.message.reply_text(f"❌ {str(ve)}")

#     except Exception as e:
#         print(f"Unexpected error for user {user_id}: {str(e)}")
#         await update.message.reply_text("❌ یک خطای غیرمنتظره رخ داده است. لطفاً دوباره تلاش کنید.")




# def fetch_info(link: str):
#     try:
#         search_query = scholarly.search_pubs(link)
#         article = next(search_query)
#         bib = article.get('bib', {})
#         return {
#             "title": bib.get('title', 'عنوان ناموجود'),
#             "abstract": bib.get('abstract', 'چکیده‌ای در دسترس نیست.'),
#             "authors": bib.get('author', 'نویسندگان مشخص نشده‌اند.'),
#             "pub_year": bib.get('pub_year', 'سال انتشار مشخص نشده است.'),
#             "pub_url": article.get('pub_url', 'لینک موجود نیست.'),
#         }
#     except StopIteration:
#         raise ValueError("هیچ مقاله‌ای با این لینک پیدا نشد.")
#     except Exception as e:
#         print(f"Error in fetch_article_info: {str(e)}")
#         raise ValueError("خطایی در دریافت اطلاعات مقاله رخ داد.")


# def generate_summary(article_info: dict):
#     try:
#         article_details = (
#             f"**عنوان:** {article_info['title']}\n\n"
#             f"**چکیده:** {article_info['abstract']}\n\n"
#             f"**نویسنده(ها):** {article_info['authors']}\n\n"
#             f"**سال انتشار:** {article_info['pub_year']}\n\n"
#             f"**لینک مقاله:** {article_info['pub_url']}"
#         )
#         response = model.generate_content(f"""

# مقاله زیر رو بررسی کن و یک خلاصه خیلی کامل ازش بفرست واسم.
# خلاصه‌ای که مینویسی به زبان عامیانه و روان فارسی باشه.

# {article_details}
#         """)
#         return response.text
#     except Exception as e:
#         print(f"Error in generate_summary: {str(e)}")
#         raise ValueError("خطایی در خلاصه‌سازی مقاله رخ داد.")


