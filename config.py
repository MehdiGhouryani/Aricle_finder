from telegram import Bot

ADMIN_CHAT_ID=['1717599240']
BOT_USERNAME = "MaghaleBazbot"



def reset_user_data(context):
    if context.user_data:
        for key in context.user_data.keys():
            context.user_data[key] = False

async def send_error_to_admin(error_message):
    admin_user_id = 1717599240
    try:
       await Bot.send_message(admin_user_id, error_message)
    except Exception as e:
        print(f"Failed to send error message to admin: {str(e)}")
