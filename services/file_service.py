import aiohttp
from telegram import Bot

async def download_pdf(pdf_url: str, user_id: int) -> str:

    async with aiohttp.ClientSession() as session:
        async with session.get(pdf_url) as response:
            if response.status == 200:
                file_path = f"/tmp/article_{user_id}.pdf"
                with open(file_path, 'wb') as file:
                    file.write(await response.read())
                return file_path
            raise Exception("Failed to download the PDF.")

async def send_file_to_user(file_path: str, user_id: int, bot: Bot) -> None:
    """
    ارسال فایل PDF دانلودشده به کاربر در تلگرام
    """
    await bot.send_document(chat_id=user_id, document=open(file_path, 'rb'))
