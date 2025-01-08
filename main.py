from telegram.ext import Application
from handlers.start_handler import start_handler
from handlers.message_handler import message_handler
from handlers.stats_handler import stats_handler
from handlers.auto_article_handler import auto_article_task
import logging
# from scheduler import start_scheduler
from database import init_db
import os
from dotenv import load_dotenv

load_dotenv()

logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s', level=logging.INFO)
TOKEN = os.getenv('TOKEN')


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
