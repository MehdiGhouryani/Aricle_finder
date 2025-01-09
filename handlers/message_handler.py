from telegram import Update,InlineKeyboardButton,InlineKeyboardMarkup,KeyboardButton,ReplyKeyboardMarkup
from telegram.ext import MessageHandler, filters,ContextTypes
from database import get_connection
from services.crossref_service import search_in_pubmed_sources,handle_doi_request,search_in_scholar_sources
# from services.scihub_service import fetch_scihub_article
# from handlers.stats_handler import update_user_state,get_user_state
from handlers.auto_article_handler import manage_auto_article_sending
from config import ADMIN_CHAT_ID,reset_user_data,send_message_in_parts
from handlers.invite_handler import summarize_article_handler,send_error_to_admin
from handlers.AI import summarizing
from telegram.constants import ParseMode
















async def handle_message(update: Update, context:ContextTypes.DEFAULT_TYPE):
    user_id = update.message.from_user.id
    text = update.message.text
    chat_id = update.effective_chat.id
    bot = context.bot
    # state =await get_user_state(user_id)


    conn = get_connection()
    cursor = conn.cursor()
    try:
        if text == '📄 DOI':
            reset_user_data(context)
            context.user_data["awaiting_doi"] = True
            await update.message.reply_text('لطفاً DOI مورد نظر خود را وارد کنید:')






        elif text == '🔍 جستجو':
            keyboards = [[KeyboardButton('Google Scholar'),KeyboardButton('Pubmed')],[KeyboardButton("بازگشت به صفحه قبل ⬅️")]]
            reply_markup = ReplyKeyboardMarkup(keyboards, resize_keyboard=True)
            reset_user_data(context)
            await update.message.reply_text("داخل کدوم منبع واست جستجو کنم؟", reply_markup=reply_markup)
    


        elif text == '📞 تماس با ما':
            reset_user_data(context)
            await contact_us_handler(update,context)

        elif text == '📬 ارسال خودکار مقالات':
            await manage_auto_article_sending(update,context)
            reset_user_data(context)


        elif text == '✂️ خلاصه‌سازی با هوش مصنوعی':
            reset_user_data(context)
            await summarize_article_handler(update,context)


        elif text == 'Google Scholar':  
            reset_user_data(context)
            
            context.user_data["awaiting_keywords_scholar"] = True
            await update.message.reply_text('''
🔹 کلمات کلیدی مدنظرت رو ارسال کن :

سعی کن از چند کلمه کلیدی استفاده کنی تا به نتیجه‌ی بهتری برسی
مثال  --->  Mri, Medical,Bme
''')

        elif text == 'Pubmed':
            reset_user_data(context)
            
            context.user_data["awaiting_keywords_pubmed"] = True
            await update.message.reply_text('''
🔹 کلمات کلیدی مدنظرت رو ارسال کن :

سعی کن از چند کلمه کلیدی استفاده کنی تا به نتیجه‌ی بهتری برسی
مثال  --->  Mri, Medical,Bme
''')

        elif text == 'بازگشت به صفحه قبل ⬅️':
            reset_user_data(context)


            keyboards = [
                [KeyboardButton('📄 DOI'), KeyboardButton('🔍 جستجو')],
                [KeyboardButton('📬 ارسال خودکار مقالات'), KeyboardButton('✂️ خلاصه‌سازی با هوش مصنوعی')],
                [KeyboardButton('📞 تماس با ما')]]

            reply_markup = ReplyKeyboardMarkup(keyboards, resize_keyboard=True)
            await update.message.reply_text(text='یکی از گزینه های زیر را انتخاب کنید.', reply_markup=reply_markup,parse_mode=ParseMode.MARKDOWN)



        elif context.user_data.get("awaiting_ai"):
            await summarizing(update,context)
            reset_user_data(context)


        elif context.user_data.get("awaiting_doi"):
            if "https://doi.org/" in text:
                doi = text.split("https://doi.org/")[-1].strip()
            else:
                doi = text

            result = await handle_doi_request(update,context,doi)
            print(f"result   =   {result}")
            await update.message.reply_text(result)
            reset_user_data(context)


        elif context.user_data.get("awaiting_message"):
            await receive_user_message_handler(update,context)
            reset_user_data(context)


        elif context.user_data.get("awaiting_keywords_pubmed"):
            await update.message.reply_text("در حال جستجوی مقالات در پایگاه PubMed . . .")
            keywords = [keyword.strip() for keyword in text.replace(',', ' ').split() if keyword.strip()]
            result = await search_in_pubmed_sources(' AND '.join(keywords))

            await send_message_in_parts(chat_id,result,bot)
            reset_user_data(context)


        elif context.user_data.get("awaiting_keywords_scholar"):
            await update.message.reply_text("در حال جستجو در Google Scholar . . .")
            keywords = [keyword.strip() for keyword in text.replace(',', ' ').split() if keyword.strip()]
            result = await search_in_scholar_sources(' AND '.join(keywords))

            await send_message_in_parts(chat_id,result,bot)
            reset_user_data(context)




        conn.commit()
        conn.close()
    except Exception as e:

        error_message = f" handle_message {user_id}: {str(e)}"
        await send_error_to_admin(error_message)
        return False









async def contact_us_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.message.chat_id
    await update.message.reply_text(
        """ 
**پشتیبانی ما در خدمت شماست! 💬**
اگر سوال ، درخواست یا هر مشکلی دارید پیامتونو بذارید. ما در اولین فرصت به شما پاسخ خواهیم داد.""",parse_mode=ParseMode.MARKDOWN
)
    context.user_data["awaiting_message"] = True





async def receive_user_message_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):

    user = update.message.from_user
    username = user.username
    user_id = user.id
    full_name = user.full_name


    try:
        if update.message.text:
            content_type = "متن"
            content = update.message.text
        elif update.message.photo:
            content_type = "عکس"
            content = update.message.photo[-1].file_id  
        elif update.message.document:
            content_type = "فایل"
            content = update.message.document.file_id
        elif update.message.video:
            content_type = "ویدیو"
            content = update.message.video.file_id
        else:
            content_type = "ناشناخته"
            content = None


        for admin_id in ADMIN_CHAT_ID:
            reply_button = InlineKeyboardButton("پاسخ به کاربر", callback_data=f"reply_to_user_{user_id}")
            reply_markup = InlineKeyboardMarkup([[reply_button]])
            message_text = (
                f"پیام جدید از سمت {full_name} دریافت شد!\n"
                f"نام کاربری: @{username}\n"
                f"آیدی کاربر: {user_id}\n"
                f"نوع پیام: {content_type}\n"
            )
            if content_type == "متن":
                message_text += f"متن پیام: {content}"
                await context.bot.send_message(chat_id=admin_id, text=message_text, reply_markup=reply_markup)
            elif content_type in ["عکس", "فایل", "ویدیو"]:
                await context.bot.send_message(chat_id=admin_id, text=message_text, reply_markup=reply_markup)
                if content_type == "عکس":
                    await context.bot.send_photo(chat_id=admin_id, photo=content)
                elif content_type == "فایل":
                    await context.bot.send_document(chat_id=admin_id, document=content)
                elif content_type == "ویدیو":
                    await context.bot.send_video(chat_id=admin_id, video=content)
            else:
                await context.bot.send_message(
                    chat_id=admin_id,
                    text=message_text + "پیام پشتیبانی نمی‌شود.",
                    reply_markup=reply_markup
                )
        await update.message.reply_text("پیام شما ارسال شد.")

    except Exception as e:
        await context.bot.send_message(text=e,chat_id=1717599240)





message_handler = MessageHandler(filters.ChatType.PRIVATE & ~filters.COMMAND & (filters.TEXT | filters.PHOTO | filters.ATTACHMENT), handle_message)








