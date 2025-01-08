from telegram import Update,InlineKeyboardButton,InlineKeyboardMarkup
from telegram.ext import MessageHandler, filters,ContextTypes
from database import get_connection
from services.crossref_service import search_in_multiple_sources,handle_doi_request
# from services.scihub_service import fetch_scihub_article
# from handlers.stats_handler import update_user_state,get_user_state
from handlers.auto_article_handler import manage_auto_article_sending
from config import ADMIN_CHAT_ID,reset_user_data
from handlers.invite_handler import summarize_article_handler,send_error_to_admin
from handlers.AI import summarizing

















async def handle_message(update: Update, context:ContextTypes.DEFAULT_TYPE):
    user_id = update.message.from_user.id
    text = update.message.text
    # state =await get_user_state(user_id)


    conn = get_connection()
    cursor = conn.cursor()
    try:
        if text == '📄 DOI':
            reset_user_data(context)
            context.user_data["awaiting_doi"] = True
            await update.message.reply_text('لطفاً DOI مورد نظر خود را وارد کنید:')





        elif text == '🔍 جستجو':
            context.user_data["awaiting_keywords"] = True
            # cursor.execute('UPDATE users SET state = ? WHERE id = ?', ('awaiting_keywords', user_id))
            await update.message.reply_text('کلمات کلیدی مدنظر خود را وارد کنید (با کاما جدا کنید):')
    


        elif text == '📞 تماس با ما':
            await contact_us_handler(update,context)



        elif text == '📬 ارسال خودکار مقالات':
            await manage_auto_article_sending(update,context)
            reset_user_data(context)




        elif text == '✂️ خلاصه‌سازی با هوش مصنوعی':
            reset_user_data(context)
            await summarize_article_handler(update,context)





        elif context.user_data.get("awaiting_ai"):
            await summarizing(update,context)
            reset_user_data(context)




        elif context.user_data.get("awaiting_doi"):
            if "https://doi.org/" in text:
                doi = text.split("https://doi.org/")[-1].strip()
            else:
                doi = text

            result = await handle_doi_request(update,context,doi)
            await update.message.reply_text(result)
            reset_user_data(context)



        elif context.user_data.get("awaiting_message"):
            await receive_user_message_handler(update,context)
            reset_user_data(context)



        elif context.user_data.get("awaiting_keywords"):
            keywords = [keyword.strip() for keyword in text.replace(',', ' ').split() if keyword.strip()]
            result = await search_in_multiple_sources(' AND '.join(keywords))

            await update.message.reply_text(result)
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
اگر سوال ، درخواست یا هر مشکلی دارید پیامتونو بذارید. ما در اولین فرصت به شما پاسخ خواهیم داد."""
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








