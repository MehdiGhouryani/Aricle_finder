from telegram import Update, KeyboardButton, ReplyKeyboardMarkup
from telegram.ext import CommandHandler,ContextTypes
from database import get_connection,save_user_data,increment_invite_count
from handlers.invite_handler import (send_error_to_admin,add_points,is_already_referred,record_referral,register_user,user_exists)
from telegram.constants import ParseMode






async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.message.from_user
    user_id = user.id
    chat_id = update.message.chat.id
    username = user.username
    name = user.full_name

    start_text ='''
**سلام! خوش اومدی به ربات مقاله‌یاب!** 😊

**🔹 دریافت با DOI:** اگه شناسه DOI مقاله داری، اینجا وارد کن و مقاله رو بگیر.

🔹 جستجو:** فقط کلمات کلیدی مقاله رو داری؟ یا دنبال مقاله‌ی تو حوزه خاصی هستی؟**
بزن و مقاله‌های مرتبط رو پیدا کن.

🔹 مقالات جدید:** مقالات جدید و مرتبط خودکار برات ارسال می‌شه.**

🔹 خلاصه‌سازی: **لینک مقاله رو بده، هوش‌مصنوعیه ربات برات خلاصه‌ش می‌کنه.**

🔹 تماس:** سوال پیشنهاد یا درخواستی داری؟  با این دکمه با ما در تماس باش.**

هر سوالی بود، ما اینجاییم!
'''

    save_user_data(user_id, chat_id, username)

    if not user_exists(user_id):
        register_user(user_id) 

        args = context.args
        if args:
            inviter_id = args[0]  
            if inviter_id.isdigit() and user_exists(int(inviter_id)) and int(inviter_id) != user_id:
                inviter_id = int(inviter_id)

                if not is_already_referred(inviter_id, user_id):
                    add_points(inviter_id, 80)  # افزایش امتیاز کاربر دعوت‌کننده
                    record_referral(inviter_id, user_id)  # ثبت دعوت در دیتابیس
                    await context.bot.send_message(chat_id=inviter_id, text="🎉 شما 50 امتیاز بابت دعوت کاربر جدید دریافت کردید!")


    # else:
    #     await update.message.reply_text(start_text,parse_mode=ParseMode.MARKDOWN)


    keyboards = [
        [KeyboardButton('📄 DOI'), KeyboardButton('🔍 جستجو')],
        [KeyboardButton('📬 ارسال خودکار مقالات'), KeyboardButton('✂️ خلاصه‌سازی با هوش مصنوعی')],
        [KeyboardButton('📞 تماس با ما')]]

    reply_markup = ReplyKeyboardMarkup(keyboards, resize_keyboard=True)
    await update.message.reply_text(text=start_text, reply_markup=reply_markup,parse_mode=ParseMode.MARKDOWN)


start_handler = CommandHandler('start', start)