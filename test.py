import requests
from telegram import Update, KeyboardButton, ReplyKeyboardMarkup
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes

import sqlite3
import logging

logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s', level=logging.INFO)
logger = logging.getLogger(__name__)

TOKEN = '7821187888:AAGE4gJs0q5S2-Cbxsz67xU4yMoiY-2aOu4'
CROSSREF_API_URL = 'https://api.crossref.org/works/'
SEMANTIC_SCHOLAR_API_URL = 'https://api.semanticscholar.org/graph/v1/paper/search'
SCIHUB_URL = 'https://sci-hub.se/'

# تنظیم پایگاه داده SQLite
conn = sqlite3.connect('users.db', check_same_thread=False)
cursor = conn.cursor()

# ایجاد جدول کاربران و آمار
cursor.execute('''CREATE TABLE IF NOT EXISTS users (id INTEGER PRIMARY KEY, username TEXT, keywords TEXT)''')
cursor.execute('''CREATE TABLE IF NOT EXISTS stats (searches_successful INTEGER, searches_failed INTEGER)''')
conn.commit()








async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    user = update.message.from_user
    cursor.execute('INSERT OR IGNORE INTO users (id, username, keywords) VALUES (?, ?, ?)', (user.id, user.username, None))
    conn.commit()

    keyboards = [
        [KeyboardButton('دریافت با DOI'), KeyboardButton('دریافت با کلمات کلیدی')],
        [KeyboardButton('بخش ارسال خودکار')],
    ]
    reply_markup = ReplyKeyboardMarkup(keyboards, resize_keyboard=True)
    await update.message.reply_text('سلام به ربات مقاله یاب خوش اومدین', reply_markup=reply_markup)









async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    user_id = update.message.from_user.id
    text = update.message.text
    user_message = update.message.text

    if text == 'دریافت با DOI':
        context.user_data['await_doi'] = True
        context.user_data['await_keywords'] = False 
        await update.message.reply_text('DOI مورد نظر خود را وارد کنید:')

    elif context.user_data.get('await_doi') and text not in ['دریافت با کلمات کلیدی', 'بخش ارسال خودکار']:
        if "https://doi.org/" in user_message:
            doi = user_message.split("https://doi.org/")[-1].strip()
        else:    
            doi = user_message
        result = search_in_multiple_sources(doi)
        context.user_data['await_doi'] = False
        await update.message.reply_text(result)

    elif text == 'دریافت با کلمات کلیدی':
        context.user_data['await_keywords'] = True
        context.user_data['await_doi'] = False  
        await update.message.reply_text('کلمات کلیدی مدنظر خود را وارد کنید (با کاما جدا کنید):')

    elif context.user_data.get('await_keywords') and text not in ['دریافت با DOI', 'بخش ارسال خودکار']:
        keywords = user_message.replace(',', ' ').split()
        result = search_in_multiple_sources(' AND '.join(keywords))
        context.user_data['await_keywords'] = False
        await update.message.reply_text(result)

    elif text == 'بخش ارسال خودکار':
        await update.message.reply_text("این بخش در حال توسعه است.")





# تابع برای دریافت مقاله از CrossRef با DOI
def fetch_article_by_doi(doi: str) -> str:
    response = requests.get(f"{CROSSREF_API_URL}{doi}")
    if response.status_code == 200:
        data = response.json()
        title = data['message'].get('title', ['عنوانی یافت نشد'])[0]
        authors = data['message'].get('author', [])
        
        author_names = []
        for author in authors:
            given = author.get('given', 'ناشناخته')
            family = author.get('family', '')
            author_names.append(f"{given} {family}".strip())
        
        authors_str = ', '.join(author_names) if author_names else 'ناشناخته'
        return f"📚 Title: {title}\n👨‍🔬 Authors: {authors_str}\n🔗 DOI: {doi}\n🔗 URL: {data['message'].get('URL', 'لینکی موجود نیست')}"
    else:
        return "متاسفم، مقاله‌ای با این DOI پیدا نشد."
    



# تابع برای جستجوی مقاله در Sci-Hub با DOI
def fetch_scihub_article(doi: str) -> str:
    url = f"{SCIHUB_URL}{doi}"
    return f"📰 مقاله‌ای با DOI: {doi} در Sci-Hub موجود است. می‌توانید از این لینک مشاهده کنید: {url}"

# تابع برای جستجوی مقاله در Semantic Scholar
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

# تابع برای جستجو در arXiv
def search_arxiv(keywords: str) -> str:
    url = f"http://export.arxiv.org/api/query?search_query=all:{keywords}&start=0&max_results=3"
    response = requests.get(url)
    if response.status_code == 200:
        entries = response.text.split('<entry>')[1:]
        articles = ""
        for entry in entries:
            title = entry.split('<title>')[1].split('</title>')[0]
            authors = entry.split('<name>')[1].split('</name>')[0]
            link = entry.split('<id>')[1].split('</id>')[0]
            articles += f"📚 Title: {title.strip()}\n👨‍🔬 Authors: {authors.strip()}\n🔗 URL: {link}\n\n"
        return articles if articles else "No articles found in arXiv."
    return "Error fetching articles from arXiv."


def search_pubmed(keywords: str) -> str:
    url = f"https://api.ncbi.nlm.nih.gov/lit/ctxp/v1/pubmed/?format=ris&term={keywords}"
    response = requests.get(url)
    if response.status_code == 200:
        data = response.text
        articles = ""
        for entry in data.split('\n\n'):
            if 'TI  -' in entry and 'AU  -' in entry:
                title = entry.split('TI  - ')[1].split('\n')[0]
                author = entry.split('AU  - ')[1].split('\n')[0]
                articles += f"📚 Title: {title.strip()}\n👨‍🔬 Authors: {author.strip()}\n\n"
        return articles if articles else "No articles found in PubMed."
    return "Error fetching articles from PubMed."



def search_in_multiple_sources(keywords_or_doi: str) -> str:
    if keywords_or_doi.startswith('10.'):
        result = fetch_article_by_doi(keywords_or_doi)

        if 'متاسفم' in result:
            return result
        

        
        if result:
            cursor.execute('UPDATE stats SET searches_successful = searches_successful + 1')
            conn.commit()
            return result

        # جستجو در Sci-Hub
        result = fetch_scihub_article(keywords_or_doi)
        if result:
            cursor.execute('UPDATE stats SET searches_successful = searches_successful + 1')
            conn.commit()
            return result



    keywords = ' AND '.join(keywords_or_doi.split(','))

    result = search_articles_by_keywords_scholar(keywords)
    if result:
        cursor.execute('UPDATE stats SET searches_successful = searches_successful + 1')
        conn.commit()
        return result

    result = search_articles_by_keywords_google(keywords)
    if result:
        cursor.execute('UPDATE stats SET searches_successful = searches_successful + 1')
        conn.commit()
        return result

    result = search_arxiv(keywords)
    if result:
        cursor.execute('UPDATE stats SET searches_successful = searches_successful + 1')
        conn.commit()
        return result

    result = search_pubmed(keywords)
    if result:
        cursor.execute('UPDATE stats SET searches_successful = searches_successful + 1')
        conn.commit()
        return result

    cursor.execute('UPDATE stats SET searches_failed = searches_failed + 1')
    conn.commit()
    return "هیچ مقاله‌ای برای درخواست شما پیدا نشد."



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

if __name__== '__main__':
    main()