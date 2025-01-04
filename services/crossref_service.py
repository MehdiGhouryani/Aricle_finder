import aiohttp
from scholarly import scholarly
from services.scihub_service import fetch_scihub_article
# from services.arxiv_service import 
from services.pubmed_service import search_articles_by_keywords
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
