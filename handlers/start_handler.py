from telegram import Update, KeyboardButton, ReplyKeyboardMarkup
from telegram.ext import CommandHandler,ContextTypes
from database import get_connection,save_user_data,increment_invite_count
from handlers.invite_handler import (send_error_to_admin,add_invite)


async def start(update: Update, context):
    user = update.message.from_user

    keyboards = [
        [KeyboardButton('دریافت مقاله با DOI'), KeyboardButton('جستجوی مقاله با کلمات کلیدی')],
        [KeyboardButton('ارسال خودکار مقالات جدید'),KeyboardButton('خلاصه‌سازی مقاله با هوش مصنوعی')],
        [KeyboardButton('تماس با ما')]
    ]
    reply_markup = ReplyKeyboardMarkup(keyboards, resize_keyboard=True)
    await update.message.reply_text('سلام به ربات مقاله یاب خوش آمدید!', reply_markup=reply_markup)

start_handler = CommandHandler('start', start)





async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.message.from_user
    user_id = user.id
    chat_id = update.message.chat.id
    username = user.username
    name = user.full_name


    inviter_user_id = None
    if "start=" in update.message.text:
        inviter_user_id = update.message.text.split('start=')[1]
    
    # ذخیره اطلاعات کاربر
    save_user_data(user_id, chat_id, username)

    if inviter_user_id:
        try:
            add_invite(int(inviter_user_id), user_id)
            increment_invite_count(int(inviter_user_id))  
            await update.message.reply_text(f"شما با موفقیت از لینک دعوت وارد شدید. حالا می‌توانید از قابلیت‌ها استفاده کنید!")

            # ارسال پیام به کاربر دعوت‌دهنده
            inviter_user = await context.bot.get_chat_member(chat_id=inviter_user_id, user_id=inviter_user_id)
            inviter_name = inviter_user.user.full_name
            await context.bot.send_message(
                inviter_user_id,
                f"یک نفر به نام {name} از طرف شما به ربات پیوست و حالا می‌تواند از بخش خلاصه‌سازی استفاده کند."
            )

        except Exception as e:
            error_message = f"Error processing start for {user_id} with inviter {inviter_user_id}: {str(e)}"
            send_error_to_admin(error_message)
    else:
        await update.message.reply_text('سلام به ربات مقاله یاب خوش آمدید!')


    keyboards = [
        [KeyboardButton('دریافت مقاله با DOI'), KeyboardButton('جستجوی مقاله با کلمات کلیدی')],
        [KeyboardButton('ارسال خودکار مقالات جدید'), KeyboardButton('خلاصه‌سازی مقاله با هوش مصنوعی')],
        [KeyboardButton('تماس با ما')]
    ]
    reply_markup = ReplyKeyboardMarkup(keyboards, resize_keyboard=True)
    await update.message.reply_text('لطفاً از یکی از گزینه‌ها استفاده کنید:', reply_markup=reply_markup)
