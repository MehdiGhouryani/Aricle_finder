# from telegram import Update
# from telegram.ext import CommandHandler
# from database import get_connection

# async def stats(update: Update, context):
#     conn = get_connection()
#     cursor = conn.cursor()
#     cursor.execute('SELECT * FROM stats')
#     stats_data = cursor.fetchone()
#     conn.close()

#     if stats_data:
#         successful, failed = stats_data
#         await update.message.reply_text(f"📊 آمار جستجو:\n✅ موفق: {successful}\n❌ ناموفق: {failed}")
#     else:
#         await update.message.reply_text('آماری ثبت نشده است.')

# stats_handler = CommandHandler('stats', stats)



# async def update_user_state(user_id, state):
#     conn = get_connection()
#     cursor = conn.cursor()
 
#     cursor.execute('UPDATE users SET state = ? WHERE id = ?', (state, user_id))
#     conn.commit()



# async def get_user_state(user_id):
#     conn = get_connection()
#     cursor = conn.cursor()
 
#     cursor.execute('SELECT state FROM users WHERE id = ?', (user_id,))
#     result = cursor.fetchone()
#     return result[0] if result else None
