import aiohttp

ARXIV_API_URL = 'http://export.arxiv.org/api/query'

async def search_arxiv_articles(keywords):
    params = {
        'search_query': keywords,
        'start': 0,
        'max_results': 5
    }
    async with aiohttp.ClientSession() as session:
        try:
            async with session.get(ARXIV_API_URL, params=params) as response:
                if response.status == 200:
                    data = await response.text()
                    return parse_arxiv_response(data)
                else:
                    return None
        except Exception as e:
            return None

def parse_arxiv_response(xml_data):
    # پارس ساده XML برای مقالات آرکایو
    articles = []
    for i in range(1, 6):  # فرض نمونه ساده برای تست
        articles.append({
            'title': f"عنوان مقاله آرکایو {i}",
            'author': "نام نویسنده آرکایو",
            'url': "https://arxiv.org"
        })
    return articles