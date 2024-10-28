from scholarly import scholarly
import os
import sqlite3
import logging
import requests
import aiohttp
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, KeyboardButton, ReplyKeyboardMarkup
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes


logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s', level=logging.INFO)
logger = logging.getLogger(__name__)


TOKEN = os.getenv('7821187888:AAGE4gJs0q5S2-Cbxsz67xU4yMoiY-2aOu4')


CROSSREF_API_URL = 'https://api.crossref.org/works/'
SEMANTIC_SCHOLAR_API_URL = 'https://api.semanticscholar.org/graph/v1/paper/search'
SCIHUB_URL = 'https://sci-hub.se/'


conn = sqlite3.connect('users.db', check_same_thread=False)
cursor = conn.cursor()


cursor.execute('''CREATE TABLE IF NOT EXISTS users (id INTEGER PRIMARY KEY, username TEXT, keywords TEXT, state TEXT)''')
cursor.execute('''CREATE TABLE IF NOT EXISTS stats (searches_successful INTEGER, searches_failed INTEGER)''')
cursor.execute('''CREATE TABLE IF NOT EXISTS auto_article (chat_id INTEGER ,keywords TEXT''')
conn.commit()


def update_user_state(user_id, state):
    cursor.execute('UPDATE users SET state = ? WHERE id = ?', (state, user_id))
    conn.commit()


def get_user_state(user_id):
    cursor.execute('SELECT state FROM users WHERE id = ?', (user_id,))
    result = cursor.fetchone()
    return result[0] if result else None


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    user = update.message.from_user
    cursor.execute('INSERT OR IGNORE INTO users (id, username, keywords, state) VALUES (?, ?, ?, ?)', (user.id, user.username, None, None))
    conn.commit()

    keyboards = [
        [KeyboardButton('دریافت با DOI'), KeyboardButton('دریافت با کلمات کلیدی')],
        [KeyboardButton(' ارسال خودکار مقالات ')],
    ]
    reply_markup = ReplyKeyboardMarkup(keyboards, resize_keyboard=True)
    await update.message.reply_text('سلام به ربات مقاله یاب خوش اومدین', reply_markup=reply_markup)







async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    user_id = update.message.from_user.id
    text = update.message.text
    user_message = update.message.text

    if text == 'دریافت با DOI':
        update_user_state(user_id, 'awaiting_doi')
        await update.message.reply_text('DOI مورد نظر خود را وارد کنید:')

    elif text == 'دریافت با کلمات کلیدی':
        update_user_state(user_id, 'awaiting_keywords')
        await update.message.reply_text('کلمات کلیدی مدنظر خود را وارد کنید (با کاما جدا کنید):')

    elif text == ' ارسال خودکار مقالات ':
        await manage_auto_article_sending(update,context)

    else:
        state = get_user_state(user_id)
        if state == 'awaiting_doi':
            if "https://doi.org/" in user_message:
                doi = user_message.split("https://doi.org/")[-1].strip()
            else:
                doi = user_message
            result = await search_in_multiple_sources(doi)
            update_user_state(user_id, None)
            await update.message.reply_text(result)

        elif state == 'awaiting_keywords':
            keywords = user_message.replace(',', ' ').split()
            result = await search_in_multiple_sources(' AND '.join(keywords))
            update_user_state(user_id, None)
            await update.message.reply_text(result)



def save_keyword_for_user(chat_id,keywords):
    
    conn = sqlite3.connect('users.db', check_same_thread=False)
    cursor = conn.cursor()
    cursor.execute('INSERT OR REPLACE INTO auto_article (chat_id,keywords) VSLUES ( ?, ?)',(chat_id,keywords))
    conn.commit()
    conn.close()


def remove_subscriber(chat_id):
    conn = sqlite3.connect('subscribers.db')
    cursor = conn.cursor()

    cursor.execute(f'DELETE FROM  WHERE chat_id = ?', (chat_id,))
    conn.commit()
    conn.close()






async def manage_auto_article_sending(update:Update,context:ContextTypes.DEFAULT_TYPE):
    user_id = update.message.from_user.id
    state = get_user_state(user_id)

    if state is None:
        update_user_state(user_id,'awaiting_keywords')
        await update.message.reply_text('کلمات کلیدی خود را وارد کنید ( کلمات را با کاما , جدا کنید)')
    else :
        await update.message.reply_text('شما قبلا در این بخش عضو شدید!')




async def check_new_article():
    while True:
        cursor.execute('SELECT user_id , keywords FROM auto_article')
        users =cursor.fetchall()

        for user_id , keywords in users:
            new_article = await search_in_multiple_sources(keywords)

            if new_article:
                await send_articles_to_user(user_id,new_article)

        await asyncio.sleep(24 * 3600)






async def send_articles_to_user(user_id,articles):
    cursor.execute('SELECT username FROM users WHERE id = ?'(user_id,))
    username = cursor.fetchone()[0]

    if username:






async def search_in_multiple_sources(keywords_or_doi: str) -> str:
    if keywords_or_doi.startswith('10.'):
        result = await fetch_article_by_doi(keywords_or_doi)
        if result:
            cursor.execute('UPDATE stats SET searches_successful = searches_successful + 1')
            conn.commit()
            return result


        result = fetch_scihub_article(keywords_or_doi)
        if result:
            cursor.execute('UPDATE stats SET searches_successful = searches_successful + 1')
            conn.commit()
            return result
    else:
        keywords = ' AND '.join(keywords_or_doi.split(','))
        result = await search_articles_by_keywords_scholar(keywords)
        if result:
            cursor.execute('UPDATE stats SET searches_successful = searches_successful + 1')
            conn.commit()
            return result

        result = await search_articles_by_keywords_google(keywords)
        if result:
            cursor.execute('UPDATE stats SET searches_successful = searches_successful + 1')
            conn.commit()
            return result

        result = await search_arxiv(keywords)
        if result:
            cursor.execute('UPDATE stats SET searches_successful = searches_successful + 1')
            conn.commit()
            return result

        result = await search_pubmed(keywords)
        if result:
            cursor.execute('UPDATE stats SET searches_successful = searches_successful + 1')
            conn.commit()
            return result

    cursor.execute('UPDATE stats SET searches_failed = searches_failed + 1')
    conn.commit()
    return "هیچ مقاله‌ای برای درخواست شما پیدا نشد."





async def fetch_article_by_doi(doi: str) -> str:
    async with aiohttp.ClientSession() as session:
        async with session.get(f"{CROSSREF_API_URL}{doi}") as response:
            if response.status == 200:
                data = await response.json()
                title = data['message'].get('title', ['عنوانی یافت نشد'])[0]
                authors = data['message'].get('author', [])

                author_names = [f"{author.get('given', 'ناشناخته')} {author.get('family', '')}".strip() for author in authors]
                authors_str = ', '.join(author_names) if author_names else 'ناشناخته'

                # دکمه دانلود PDF
                pdf_link = data['message'].get('URL', 'لینکی موجود نیست')
                return f"📚 عنوان: {title}\n👨‍🔬 نویسندگان: {authors_str}\n🔗 DOI: {doi}\n🔗 URL: {pdf_link}"

            return "متاسفم، مقاله‌ای با این DOI پیدا نشد."


def fetch_scihub_article(doi: str) -> str:
    url = f"{SCIHUB_URL}{doi}"
    return f"📰 مقاله‌ای با DOI: {doi} در Sci-Hub موجود است. می‌توانید از این لینک مشاهده کنید: {url}"


async def search_articles_by_keywords_scholar(keywords: str) -> str:
    async with aiohttp.ClientSession() as session:
        async with session.get(f"{SEMANTIC_SCHOLAR_API_URL}?query={keywords}&limit=3") as response:
            if response.status == 200:
                data = await response.json()
                articles = ""
                for paper in data['data']:
                    title = paper['title']
                    authors = ', '.join(paper['authors'])
                    url = paper['url']
                    articles += f"📚 عنوان: {title}\n👨‍🔬 نویسندگان: {authors}\n🔗 URL: {url}\n\n"
                return articles if articles else "مقاله‌ای یافت نشد."


async def search_articles_by_keywords_google(keywords: str) -> str:
    search_query = scholarly.search_pubs(keywords)
    articles = ""
    for result in search_query:
        title = result['bib']['title']
        authors = result['bib'].get('author', 'Unknown')
        url = result.get('pub_url', 'No URL available')
        articles += f"📚 عنوان: {title}\n👨‍🔬 نویسندگان: {authors}\n🔗 URL: {url}\n\n"
        return articles if articles else "مقاله‌ای یافت نشد."


async def search_arxiv(keywords: str) -> str:
    url = f"http://export.arxiv.org/api/query?search_query=all:{keywords}&start=0&max_results=3"


    async with aiohttp.ClientSession() as session:
        async with session.get(url) as response:
            if response.status == 200:
                entries = (await response.text()).split('<entry>')[1:]
                articles = ""
                for entry in entries:
                    title = entry.split('<title>')[1].split('</title>')[0]
                    authors = entry.split('<name>')[1].split('</name>')[0]
                    link = entry.split('<id>')[1].split('</id>')[0]
                    articles += f"📚 عنوان: {title.strip()}\n👨‍🔬 نویسندگان: {authors.strip()}\n🔗 URL: {link}\n\n"
                return articles if articles else "مقاله‌ای یافت نشد."


async def search_pubmed(keywords: str) -> str:
    url = f"https://api.ncbi.nlm.nih.gov/lit/ctxp/v1/pubmed/?format=ris&term={keywords}"
    async with aiohttp.ClientSession() as session:
        async with session.get(url) as response:
            if response.status == 200:
                data = await response.text()
                articles = ""
                for entry in data.split('\n\n'):
                    if 'TI  -' in entry and 'AU  -' in entry:
                        title = entry.split('TI  - ')[1].split('\n')[0]
                        author = entry.split('AU  - ')[1].split('\n')[0]
                        articles += f"📚 عنوان: {title.strip()}\n👨‍🔬 نویسندگان: {author.strip()}\n\n"
                return articles if articles else "مقاله‌ای یافت نشد."


async def stats(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    cursor.execute('SELECT * FROM stats')
    stats_data = cursor.fetchone()
    if stats_data:
        searches_successful, searches_failed = stats_data
        await update.message.reply_text(f"📊 آمار جستجو:\n✅ جستجوهای موفق: {searches_successful}\n❌ جستجوهای ناموفق: {searches_failed}")
    else:
        await update.message.reply_text("آمار هنوز ثبت نشده است.")


def main():
    app = Application.builder().token(TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    app.add_handler(CommandHandler("stats", stats))

    cursor.execute('INSERT OR IGNORE INTO stats (searches_successful, searches_failed) VALUES (0, 0)')
    conn.commit()

    app.run_polling()

if __name__ == '__main__':
    main()