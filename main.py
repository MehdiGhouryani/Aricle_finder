import requests
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes
from scholarly import scholarly
import sqlite3
import logging


logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s',level=logging.INFO)
logger = logging.getLogger(__name__)



TELEGRAM_TOKEN = '7821187888:AAGE4gJs0q5S2-Cbxsz67xU4yMoiY-2aOu4'


CROSSREF_API_URL = 'https://api.crossref.org/works/'
SEMANTIC_SCHOLAR_API_URL = 'https://api.semanticscholar.org/graph/v1/paper/search'


conn = sqlite3.connect('users.db', check_same_thread=False)
cursor = conn.cursor()

# ایجاد جدول کاربران و آمار
cursor.execute('''CREATE TABLE IF NOT EXISTS users (id INTEGER PRIMARY KEY, username TEXT, keywords TEXT)''')
cursor.execute('''CREATE TABLE IF NOT EXISTS stats (searches_successful INTEGER, searches_failed INTEGER)''')
conn.commit()



def fetch_article_by_doi(doi: str) -> str:
    response = requests.get(f"{CROSSREF_API_URL}{doi}")
    if response.status_code == 200:
        data = response.json()
        title = data['message']['title'][0]
        authors = ', '.join([author['given'] + ' ' + author['family'] for author in data['message']['author']])
        return f"📚 Title: {title}\n👨‍🔬 Authors: {authors}\n🔗 DOI: {doi}\n🔗 URL: {data['message']['URL']}"
    return None



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

# تابع برای جستجو در Google Scholar
def search_articles_by_keywords_google(keywords: str) -> str:
    search_query = scholarly.search_pubs(keywords)
    articles = ""
    for result in search_query:
        title = result['bib']['title']
        authors = result['bib'].get('author', 'Unknown')
        url = result.get('pub_url', 'No URL available')
        articles += f"📚 Title: {title}\n👨‍🔬 Authors: {authors}\n🔗 URL: {url}\n\n"
        return articles if articles else None

# تابع ترکیبی برای جستجوی مقاله در منابع مختلف
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

# هندلر شروع برای کاربر
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    user = update.message.from_user
    cursor.execute('INSERT OR IGNORE INTO users (id, username, keywords) VALUES (?, ?, ?)', (user.id, user.username, None))
    conn.commit()
    await update.message.reply_text('سلام! لطفاً DOI یا کلمات کلیدی خود را ارسال کنید.')

# هندلر برای دریافت کلمات کلیدی از کاربران
async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    user_input = update.message.text
    user_id = update.message.from_user.id


# ذخیره کلمات کلیدی برای ارسال خودکار
    if not user_input.startswith('10.'):
        cursor.execute('UPDATE users SET keywords = ? WHERE id = ?', (user_input, user_id))
        conn.commit()
        await update.message.reply_text(f"کلمات کلیدی شما برای ارسال خودکار ذخیره شد: {user_input}")
    
    result = search_in_multiple_sources(user_input)
    await update.message.reply_text(result)

# هندلر برای ادمین (دریافت آمار)
async def stats(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    cursor.execute('SELECT * FROM stats')
    stats_data = cursor.fetchone()
    if stats_data:
        searches_successful, searches_failed = stats_data
        await update.message.reply_text(f"📊 آمار جستجو:\n✅ جستجوهای موفق: {searches_successful}\n❌ جستجوهای ناموفق: {searches_failed}")
    else:
        await update.message.reply_text("آمار هنوز ثبت نشده است.")

# تابع برای حذف کلمات کلیدی و لغو ارسال خودکار
async def stop_auto_send(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    user_id = update.message.from_user.id
    cursor.execute('UPDATE users SET keywords = NULL WHERE id = ?', (user_id,))
    conn.commit()
    await update.message.reply_text("ارسال خودکار مقالات برای شما متوقف شد. برای فعال‌سازی مجدد، کلمات کلیدی جدیدی ارسال کنید.")

# تنظیم ربات و استارت هندلرها
def main() -> None:
    # ساختن اپلیکیشن تلگرام با استفاده از نسخه جدید
    application = Application.builder().token(TELEGRAM_TOKEN).build()

    # ثبت دستورات و هندلرها
    application.add_handler(CommandHandler("start", start))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

    # هندلر برای ادمین
    application.add_handler(CommandHandler("stats", stats))

    # هندلر برای لغو ارسال خودکار
    application.add_handler(CommandHandler("stop", stop_auto_send))

    # شروع به کار ربات
    application.run_polling()

if __name__ == '__main__':
    # ثبت آمار اولیه در دیتابیس (در صورت نبود)
    cursor.execute('INSERT OR IGNORE INTO stats (searches_successful, searches_failed) VALUES (0, 0)')
    conn.commit()

    main()