import aiohttp
from scholarly import scholarly
from services.scihub_service import fetch_scihub_article
from config import send_error_to_admin
from database import get_connection

CROSSREF_API_URL = 'https://api.crossref.org/works/'
SEMANTIC_SCHOLAR_API_URL = 'https://api.semanticscholar.org/graph/v1/paper/search'



from telegram import Update, Bot
from telegram.ext import ContextTypes
from services.file_service import download_pdf, send_file_to_user
import os

async def handle_doi_request(update: Update, context: ContextTypes.DEFAULT_TYPE,doi):

    user_id = update.message.chat_id
    # doi = doi.strip()
    try:
        if not doi.startswith("10."):
            await update.message.reply_text("لطفاً یک DOI معتبر وارد کنید.")
            return

        article_data = await fetch_pdf_link_by_doi(doi)

        if article_data["message"] == "Open Access":
            pdf_link = article_data["pdf_link"]

            file_path = await download_pdf(pdf_link, user_id)


            await send_file_to_user(file_path, user_id, context.bot)

            try:
                os.remove(file_path)
            except Exception as e:
                print(f"Error deleting file {file_path}: {e}")

        else:
            await update.message.reply_text("مقاله برای دانلود در دسترس نیست !")
            result = await fetch_article_by_doi(doi)
            await update.message.reply_text(f"{result}\n\n\n میتونی DOI رو بفرستی بخش خلاصه سازی و هوش مصنوعی واست ی خلاصه ازش بده ")

    except Exception as e:
        print(f"Error in handling DOI request: {e}")
        await update.message.reply_text(f"خطایی رخ داد: {e}\nلطفاً دوباره تلاش کنید.")




async def fetch_article_by_doi(doi: str) -> str:
    async with aiohttp.ClientSession() as session:
        async with session.get(f"{CROSSREF_API_URL}{doi}") as response:
            try:
                if response.status == 200:
                    data = await response.json()
                    title = data['message'].get('title', ['عنوانی یافت نشد'])[0]
                    authors = data['message'].get('author', [])

                    author_names = [f"{author.get('given', 'ناشناخته')} {author.get('family', '')}".strip() for author in authors]
                    authors_str = ', '.join(author_names) if author_names else 'ناشناخته'

                    pdf_link = data['message'].get('URL', 'لینکی موجود نیست')
                    # abstract = data['message'].get('abstract', 'چکیده‌ای موجود نیست')

                    return f"📚 عنوان: {title}\n👨‍🔬 نویسندگان: {authors_str}\n🔗 DOI: {doi}\n🔗 URL: {pdf_link}"

                return "متاسفم، مقاله‌ای با این DOI پیدا نشد."
            except Exception as e:
                error_message = f"Error fetch article by doi  : {str(e)}"
                await send_error_to_admin(error_message)


async def fetch_article_by_doi_for_ai(doi: str) -> str:
    async with aiohttp.ClientSession() as session:
        async with session.get(f"{CROSSREF_API_URL}{doi}") as response:
            try:
                if response.status == 200:
                    data = await response.json()
                    title = data['message'].get('title', ['عنوانی یافت نشد'])[0]
                    abstract = data['message'].get('abstract', 'چکیده‌ای موجود نیست')

                    return f"📚 عنوان: {title}\n👨‍🔬 نویسندگان:\n\n📝 چکیده: {abstract[:600]}"

                return "متاسفم، مقاله‌ای با این DOI پیدا نشد."
            except Exception as e:
                error_message = f"Error fetch article by doi  : {str(e)}"
                await send_error_to_admin(error_message)


UNPAYWALL_API_URL = "https://api.unpaywall.org/v2/"
EMAIL_FOR_UNPAYWALL = "mohammadmahdi670@gmail.com"  # ایمیل ثبت‌شده در Unpaywall

async def fetch_pdf_link_by_doi(doi: str) -> dict:
    async with aiohttp.ClientSession() as session:
        async with session.get(f"{UNPAYWALL_API_URL}{doi}?email={EMAIL_FOR_UNPAYWALL}") as response:
            if response.status == 200:
                data = await response.json()
                
                best_oa_location = data.get('best_oa_location', {})
                pdf_link = best_oa_location.get('url_for_pdf')
                publisher_page = best_oa_location.get('url')
                
                return {
                    "pdf_link": pdf_link or None,
                    "publisher_page": publisher_page or None,
                    "message": "Open Access" if pdf_link else "Not Open Access"
                }
            else:
                return {"message": f"Error: {response.status} - DOI not found"}



async def search_in_multiple_sources(keywords_or_doi: str) -> str:
    
    conn = get_connection()
    cursor = conn.cursor()

    keywords = ' AND '.join(keywords_or_doi.split(','))
    try:
        result = await search_articles_by_keywords_google(keywords)
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
    except Exception as e:
        print(f"ERROR IN SEARCH MULTIPLE SOURCE  ======> {e}")


async def search_articles_by_keywords_google(keywords: str) -> str:
    try:
        search_query = scholarly.search_pubs(keywords)
        
        articles = ""
        max_results = 5  # محدودیت تعداد نتایج
        count = 0

        for result in search_query:
            if count >= max_results:
                break

            # عنوان مقاله
            title = result['bib'].get('title', 'عنوانی یافت نشد')

            # نویسندگان
            authors_list = result['bib'].get('author', [])
            if authors_list:
                authors = ', '.join(authors_list)
            else:
                authors = "نویسندگان ناشناس"

            # لینک مقاله
            url = result.get('pub_url')
            if not url:
                url = f"https://www.google.com/search?q={title.replace(' ', '+')}"

            # افزودن به خروجی
            count += 1
            articles += (
                f"🔹 مقاله شماره {count}:\n"
                f"📚 عنوان: {title}\n"
                f"👨‍🔬 نویسندگان: {authors}\n"
                f"🔗 URL: {url}\n\n"
            )

        return articles if articles else "مقاله‌ای یافت نشد."

    except Exception as e:
        print(f"خطا در تابع search_articles_by_keywords_google: {e}")
        return "خطایی رخ داد. لطفاً دوباره تلاش کنید."




async def search_articles_by_keywords(keywords: str) -> str:
    query = '+'.join(keywords.split())
    url = f"{CROSSREF_API_URL}?query={query}&rows=5"
    
    async with aiohttp.ClientSession() as session:
        async with session.get(url) as response:
            if response.status == 200:
                data = await response.json()
                articles = ""
                for item in data['message']['items']:
                    title = item['title'][0] if 'title' in item else 'عنوانی یافت نشد'
                    authors = ', '.join([author['given'] + ' ' + author['family'] for author in item.get('author', [])])
                    url = item.get('URL', 'لینکی موجود نیست')
                    articles += f"📚 عنوان: {title}\n👨‍🔬 نویسندگان: {authors}\n🔗 URL: {url}\n\n"
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




