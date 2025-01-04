from telegram import Update
from telegram.ext import MessageHandler, filters,ContextTypes
from database import get_connection
from services.crossref_service import fetch_article_by_doi,search_in_multiple_sources
# from services.scihub_service import fetch_scihub_article
from handlers.stats_handler import update_user_state,get_user_state




async def handle_message(update: Update, context:ContextTypes.DEFAULT_TYPE):
    user_id = update.message.from_user.id
    text = update.message.text
    state =await get_user_state(user_id)


    conn = get_connection()
    cursor = conn.cursor()
    try:
        if text == 'دریافت با DOI':
            # cursor.execute('UPDATE users SET state = ? WHERE id = ?', ('awaiting_doi', user_id))
            context.user_data["awaiting_doi"] = True
            await update.message.reply_text('لطفاً DOI مورد نظر خود را وارد کنید:')


        elif text == 'دریافت با کلمات کلیدی':
            context.user_data["awaiting_keywords"] = True
            # cursor.execute('UPDATE users SET state = ? WHERE id = ?', ('awaiting_keywords', user_id))
            await update.message.reply_text('کلمات کلیدی مدنظر خود را وارد کنید (با کاما جدا کنید):')


        # elif text == ' ارسال خودکار مقالات ':
        #     await manage_auto_article_sending(update,context)





        elif context.user_data.get("awaiting_doi"):
            if "https://doi.org/" in text:
                doi = text.split("https://doi.org/")[-1].strip()
            else:
                doi = text

            result = await fetch_article_by_doi(doi)
            await update.message.reply_text(result)
            # update_user_state(user_id, None)
            context.user_data["awaiting_doi"] = None

        elif context.user_data.get("awaiting_keywords"):
            keywords = [keyword.strip() for keyword in text.replace(',', ' ').split() if keyword.strip()]
            result = await search_in_multiple_sources(' AND '.join(keywords))

            await update.message.reply_text(result)
            # await update_user_state(user_id, None)
            context.user_data["awaiting_keywords"] = None
    
        conn.commit()
        conn.close()
    except Exception as e:
        print(f"ERROR IN MESSAGE HANDLER ------------> {e}")

message_handler = MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message)








