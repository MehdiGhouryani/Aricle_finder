from telegram import Update, KeyboardButton, ReplyKeyboardMarkup
from telegram.ext import CommandHandler
from database import get_connection

async def start(update: Update, context):
    user = update.message.from_user
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute('INSERT OR IGNORE INTO users (id, username, keywords, state) VALUES (?, ?, ?, ?)', 
                   (user.id, user.username, None, None))
    conn.commit()
    conn.close()

    keyboards = [
        [KeyboardButton('دریافت با DOI'), KeyboardButton('دریافت با کلمات کلیدی')],
        [KeyboardButton('ارسال خودکار مقالات')],
    ]
    reply_markup = ReplyKeyboardMarkup(keyboards, resize_keyboard=True)
    await update.message.reply_text('سلام به ربات مقاله یاب خوش آمدید!', reply_markup=reply_markup)

start_handler = CommandHandler('start', start)
