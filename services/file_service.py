
from telegram import Bot

import aiofiles
import aiohttp
import os






async def download_pdf(pdf_url: str, user_id: int) -> str:
    """
    دانلود PDF از URL و ذخیره در مسیر موقت
    """
    file_name = f"article_{user_id}.pdf"
    file_path = os.path.join("/tmp", file_name)

    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(pdf_url, headers={"User-Agent": "Mozilla/5.0"}) as response:
                if response.status == 200:
                    async with aiofiles.open(file_path, mode='wb') as file:
                        await file.write(await response.read())
                    return file_path
                elif response.status == 403:
                    raise PermissionError("دسترسی به فایل PDF محدود شده است.")
                elif response.status == 404:
                    raise FileNotFoundError("فایل PDF یافت نشد.")
                else:
                    raise Exception(f"خطای HTTP {response.status}: دانلود PDF ناموفق بود.")
    except PermissionError as e:
        raise Exception("دسترسی به فایل محدود است. لطفاً از صفحه ناشر استفاده کنید.")
    except aiohttp.ClientError as e:
        raise Exception(f"خطای ارتباط با سرور: {e}")
    except Exception as e:
        raise Exception(f"خطای عمومی هنگام دانلود PDF: {e}")


async def send_file_to_user(file_path: str, user_id: int, bot: Bot) -> None:
    """
    ارسال فایل PDF دانلودشده به کاربر در تلگرام
    """
    try:
        # باز کردن فایل به صورت صحیح برای ارسال
        with open(file_path, 'rb') as file:
            await bot.send_document(chat_id=user_id, document=file)
    except Exception as e:
        raise Exception(f"خطا در ارسال فایل به کاربر: {e}")