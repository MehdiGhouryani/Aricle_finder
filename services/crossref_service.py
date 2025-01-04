import aiohttp
from scholarly import scholarly


CROSSREF_API_URL = 'https://api.crossref.org/works/'





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
    if keywords_or_doi.startswith('10.'):

        result = await fetch_article_by_doi(keywords_or_doi)
        return result
    else:

        result = await search_articles_by_keywords(keywords_or_doi)
        return result
    




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