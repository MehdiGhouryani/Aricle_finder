import aiohttp
from scholarly import scholarly
from services.scihub_service import fetch_scihub_article

from database import get_connection

CROSSREF_API_URL = 'https://api.crossref.org/works/'
SEMANTIC_SCHOLAR_API_URL = 'https://api.semanticscholar.org/graph/v1/paper/search'




async def fetch_article_by_doi(doi: str) -> str:
    async with aiohttp.ClientSession() as session:
        async with session.get(f"{CROSSREF_API_URL}{doi}") as response:
            if response.status == 200:
                data = await response.json()
                title = data['message'].get('title', ['عنوانی یافت نشد'])[0]
                authors = data['message'].get('author', [])

                author_names = [f"{author.get('given', 'ناشناخته')} {author.get('family', '')}".strip() for author in authors]
                authors_str = ', '.join(author_names) if author_names else 'ناشناخته'

                pdf_link = data['message'].get('URL', 'لینکی موجود نیست')
                return f"📚 عنوان: {title}\n👨‍🔬 نویسندگان: {authors_str}\n🔗 DOI: {doi}\n🔗 URL: {pdf_link}"

            return "متاسفم، مقاله‌ای با این DOI پیدا نشد."
        




async def search_in_multiple_sources(keywords_or_doi: str) -> str:
    
    conn = get_connection()
    cursor = conn.cursor()

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

        result = await search_pubmed(keywords)
        if result:
            cursor.execute('UPDATE stats SET searches_successful = searches_successful + 1')
            conn.commit()
            return result

    cursor.execute('UPDATE stats SET searches_failed = searches_failed + 1')
    conn.commit()
    return "هیچ مقاله‌ای برای درخواست شما پیدا نشد."



async def search_articles_by_keywords_scholar(keywords: str) -> str:
    try:
        url = f"{SEMANTIC_SCHOLAR_API_URL}?query={keywords}&limit=3"

        async with aiohttp.ClientSession() as session:
            async with session.get(url) as response:
                if response.status == 200:
                    data = await response.json()

                    articles = ""
                    for idx, paper in enumerate(data.get('data', []), start=1):
                        title = paper.get('title', 'عنوانی یافت نشد')

                        # مدیریت نویسندگان
                        authors_list = paper.get('authors', [])
                        if authors_list:
                            authors = ', '.join(
                                f"{author.get('firstName', '')} {author.get('lastName', '')}".strip()
                                for author in authors_list
                            )
                            if not authors.strip():
                                authors = "نویسندگان ناشناس"
                        else:
                            authors = "نویسندگان ناشناس"

                        # مدیریت لینک
                        url = paper.get('url')
                        if not url:
                            doi = paper.get('externalIds', {}).get('DOI', None)
                            if doi:
                                url = f"https://doi.org/{doi}"
                            else:
                                url = "لینکی موجود نیست"

                        # افزودن به خروجی
                        articles += (
                            f"🔹 مقاله شماره {idx}:\n"
                            f"📚 عنوان: {title}\n"
                            f"👨‍🔬 نویسندگان: {authors}\n"
                            f"🔗 URL: {url}\n\n"
                        )

                    return articles if articles else "مقاله‌ای یافت نشد."

                else:
                    return f"خطا در دریافت داده‌ها. کد وضعیت: {response.status}"
    except Exception as e:
        return f"خطایی رخ داد: {str(e)}"



async def search_articles_by_keywords_google(keywords: str) -> str:
    search_query = scholarly.search_pubs(keywords)
    articles = ""
    try:
        for result in search_query:
            title = result['bib']['title']
            authors = result['bib'].get('author', 'Unknown')
            url = result.get('pub_url', 'No URL available')
            articles += f"📚 عنوان: {title}\n👨‍🔬 نویسندگان: {authors}\n🔗 URL: {url}\n\n"
            return articles if articles else "مقاله‌ای یافت نشد."
    except Exception as e:
        print(f"IN keywords_google ---->  {e}")




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
