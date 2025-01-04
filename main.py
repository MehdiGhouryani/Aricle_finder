from telegram.ext import Application
from handlers.start_handler import start_handler
from handlers.message_handler import message_handler
from handlers.stats_handler import stats_handler
from handlers.auto_article_handler import auto_article_task
# from scheduler import start_scheduler
from database import init_db
import os

# TOKEN = os.getenv('TOKEN')
TOKEN ="7821187888:AAFCIAOfgZ6b9Jf7fOPI5Us0suzavuskXkg"

def main():
    init_db()

    # ساخت اپلیکیشن تلگرام
    app = Application.builder().token(TOKEN).build()

    app.add_handler(start_handler)
    app.add_handler(message_handler)
    app.add_handler(stats_handler)


    # start_scheduler(auto_article_task)

    app.run_polling()

if __name__ == '__main__':
    main()
