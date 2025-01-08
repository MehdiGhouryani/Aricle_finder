from telegram import Bot
import os
from dotenv import load_dotenv

load_dotenv()

TOKEN = os.getenv('TOKEN')
print(TOKEN)
bot = Bot(TOKEN)

ADMIN_CHAT_ID=['1717599240']
BOT_USERNAME = "MaghaleBazbot"



def reset_user_data(context):
    if context.user_data:
        for key in context.user_data.keys():
            context.user_data[key] = False

async def send_error_to_admin(error_message):
    admin_user_id = 1717599240
    try:
       await bot.send_message(chat_id=admin_user_id, text=f"ERROR : {str(error_message)}")
    except Exception as e:
        print(f"Failed to send error message to admin: {str(e)}")
