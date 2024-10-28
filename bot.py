import logging
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes
from transformers import pipeline

# تنظیمات لاگ
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)

# بارگذاری مدل
model = pipeline("text-generation", model="gpt2")

# تابع پاسخ به سوالات
def answer_question(question):
    response = model(question, max_length=50, num_return_sequences=1)
    return response[0]['generated_text']

# تابع شروع ربات
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await update.message.reply_text('سلام! من یک ربات هستم. سوالات ریاضی خود را بپرسید.')

# تابع دریافت پیام
async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    question = update.message.text
    answer = answer_question(question)
    await update.message.reply_text(answer)

# راه‌اندازی ربات
def main():
    # ایجاد برنامه کاربردی
    application = Application.builder().token("7938065557:AAGit2Uez9kSZ_y6XOS_5gWnjTydI4bRyTM").build()

    # اضافه کردن هندلرها
    application.add_handler(CommandHandler("start", start))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

    # شروع ربات
    application.run_polling()


if __name__ == '__main__':
    main()