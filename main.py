import requests
from telegram import Update, KeyboardButton, ReplyKeyboardMarkup
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes, JobQueue
from scholarly import scholarly
import sqlite3
import logging

# تنظیمات لاگ
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s', level=logging.INFO)
logger = logging.getLogger(__name__)

# توکن ربات
TELEGRAM_TOKEN = '7821187888:AAGE4gJs0q5S2-Cbxsz67xU4yMoiY-2aOu4'

# URLهای جستجو
CROSSREF_API_URL = 'https://api.crossref.org/works/'
SEMANTIC_SCHOLAR_API_URL = 'https://api.semanticscholar.org/graph/v1/paper/search'

# اتصال به دیتابیس SQLite
conn = sqlite3.connect('users.db', check_same_thread=False)
cursor = conn.cursor()

# ایجاد جداول دیتابیس
cursor.execute('''CREATE TABLE IF NOT EXISTS users (id INTEGER PRIMARY KEY, username TEXT, keywords TEXT)''')
cursor.execute('''CREATE TABLE IF NOT EXISTS stats (searches_successful INTEGER, searches_failed INTEGER)''')
conn.commit()

# تابع جستجوی مقاله با DOI از CrossRef
def fetch_article_by_doi(doi: str) -> str:
    response = requests.get(f"{CROSSREF_API_URL}{doi}")
    if response.status_code == 200:
        data = response.json()
        title = data['message']['title'][0]
        authors = ', '.join([author['given'] + ' ' + author['family'] for author in data['message']['author']])
        return f"📚 Title: {title}\n👨‍🔬 Authors: {authors}\n🔗 DOI: {doi}\n🔗 URL: {data['message']['URL']}"
    return None

# تابع جستجو در Semantic Scholar
def search_articles_by_keywords_scholar(keywords: str) -> str:
    response = requests.get(f"{SEMANTIC_SCHOLAR_API_URL}?query={keywords}&limit=3")
    if response.status_code == 200:
        data = response.json()
        articles = ""
        for paper in data['data']:
            title = paper['title']
            authors = ', '.join(paper['authors'])
            url = paper['url']
            articles += f"📚 Title: {title}\n👨‍🔬 Authors: {authors}\n🔗 URL: {url}\n\n"
        return articles if articles else None
    return None

# تابع جستجو در Google Scholar
def search_articles_by_keywords_google(keywords: str) -> str:
    search_query = scholarly.search_pubs(keywords)
    articles = ""
    for result in search_query:
        title = result['bib']['title']
        authors = result['bib'].get('author', 'Unknown')
        url = result.get('pub_url', 'No URL available')
        articles += f"📚 Title: {title}\n👨‍🔬 Authors: {authors}\n🔗 URL: {url}\n\n"
    return articles if articles else None

# تابع ترکیبی برای جستجو در منابع مختلف
def search_in_multiple_sources(keywords_or_doi: str) -> str:
    # جستجو در CrossRef (برای DOI)
    if keywords_or_doi.startswith('10.'):
        result = fetch_article_by_doi(keywords_or_doi)
        if result:
            cursor.execute('UPDATE stats SET searches_successful = searches_successful + 1')
            conn.commit()
            return result
    # جستجو در Semantic Scholar
    result = search_articles_by_keywords_scholar(keywords_or_doi)
    if result:
        cursor.execute('UPDATE stats SET searches_successful = searches_successful + 1')
        conn.commit()
        return result
    # جستجو در Google Scholar
    result = search_articles_by_keywords_google(keywords_or_doi)
    if result:
        cursor.execute('UPDATE stats SET searches_successful = searches_successful + 1')
        conn.commit()
        return result
    # اگر مقاله‌ای پیدا نشود
    cursor.execute('UPDATE stats SET searches_failed = searches_failed + 1')
    conn.commit()
    return "هیچ مقاله‌ای برای درخواست شما پیدا نشد."

# تابع جستجو و ارسال خودکار برای کلمات کلیدی ذخیره شده
async def auto_send_articles(context: ContextTypes.DEFAULT_TYPE):
    user_data = context.job.context
    user_id = user_data['id']
    keywords = user_data['keywords']
    result = search_in_multiple_sources(keywords)
    if result:
        try:
            await context.bot.send_message(chat_id=user_id, text=result)
        except Exception as e:
            logger.error(f"Error sending message to user {user_id}: {e}")


            # هندلر شروع
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    user = update.message.from_user
    cursor.execute('INSERT OR IGNORE INTO users (id, username, keywords) VALUES (?, ?, ?)', (user.id, user.username, None))
    conn.commit()
    keyboards = [
        [KeyboardButton('دریافت با DOI'), KeyboardButton('دریافت با کلمات کلیدی')],
        [KeyboardButton('ارسال خودکار مقالات')],
    ]
    reply_markup = ReplyKeyboardMarkup(keyboards, resize_keyboard=True)
    await update.message.reply_text('سلام به ربات مقاله یاب خوش اومدین', reply_markup=reply_markup)

# هندلر برای دریافت کلمات کلیدی یا DOI
async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    user_id = update.message.from_user.id
    text = update.message.text
    user_message = update.message.text

    if text == 'دریافت با DOI':
        context.user_data['await_doi'] = True
        await update.message.reply_text('DOI و بفرس')
    elif context.user_data.get('await_doi'):
        doi = user_message
        result = search_in_multiple_sources(doi)
        context.user_data['await_doi'] = False
        await update.message.reply_text(result)
    elif text == 'دریافت با کلمات کلیدی':
        context.user_data['await_keyboard'] = True
        await update.message.reply_text('کلمات کلیدی مد نظرت و با , (کاما) جدا کن و بفرست')
    elif context.user_data.get('await_keyboard'):
        key_art = user_message.replace(',', ' ').split()
        result = search_in_multiple_sources(" ".join(key_art))
        context.user_data['await_keyboard'] = False
        await update.message.reply_text(result)
    elif text == 'ارسال خودکار مقالات':
        await update.message.reply_text('لطفا کلمات کلیدی خود را وارد کنید تا مقالات به صورت خودکار ارسال شوند.')
        context.user_data['await_auto_send'] = True
    elif context.user_data.get('await_auto_send'):
        keywords = user_message
        cursor.execute('UPDATE users SET keywords = ? WHERE id = ?', (keywords, user_id))
        conn.commit()
        await update.message.reply_text(f"کلمات کلیدی شما ذخیره شد و مقالات مرتبط به صورت خودکار ارسال می‌شوند: {keywords}")

        # زمان‌بندی ارسال خودکار
        context.job_queue.run_repeating(auto_send_articles, interval=86400, first=0, context={'id': user_id, 'keywords': keywords})
        context.user_data['await_auto_send'] = False

# هندلر آمار
async def stats(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    cursor.execute('SELECT * FROM stats')
    stats_data = cursor.fetchone()
    if stats_data:
        searches_successful, searches_failed = stats_data
        await update.message.reply_text(f"📊 آمار جستجو:\n✅ جستجوهای موفق: {searches_successful}\n❌ جستجوهای ناموفق: {searches_failed}")
    else:
        await update.message.reply_text("آمار هنوز ثبت نشده است.")

# تابع لغو ارسال خودکار
async def stop_auto_send(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    user_id = update.message.from_user.id
    cursor.execute('UPDATE users SET keywords = NULL WHERE id = ?', (user_id,))
    conn.commit()
    await update.message.reply_text("ارسال خودکار مقالات برای شما متوقف شد")


def main():
    app = Application.builder().token(TELEGRAM_TOKEN).build() 
    app.add_handler(CommandHandler('start', start)) 
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message)) 
    app.add_handler(CommandHandler('stats', stats)) 
    app.add_handler(CommandHandler('stop', stop_auto_send)) 
    app.run_polling()

if __name__ == '__main__': 
    main()