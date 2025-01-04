import aiohttp

SCIHUB_API_URL = 'https://scihub.org/'

async def fetch_scihub_article(doi):
    async with aiohttp.ClientSession() as session:
        try:
            async with session.get(f"{SCIHUB_API_URL}{doi}") as response:
                if response.status == 200:
                    return f"📄 مقاله با DOI {doi} در Sci-Hub پیدا شد: {response.url}"
                else:
                    return "مقاله‌ای در Sci-Hub یافت نشد."
        except Exception as e:
            return f"خطا در ارتباط با Sci-Hub: {e}"
            