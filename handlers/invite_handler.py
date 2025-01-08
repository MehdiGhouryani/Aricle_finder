from telegram import Bot,Update
from telegram.ext import ContextTypes
from config import BOT_USERNAME,send_error_to_admin
import sqlite3
from datetime import date





def update_last_summary_date(user_id):
    conn = sqlite3.connect("bot.db")
    cursor = conn.cursor()
    cursor.execute('''
        UPDATE users
        SET last_summary_date = ?
        WHERE user_id = ?
    ''', (date.today(), user_id))
    conn.commit()
    conn.close()


def send_invite_link(update:Update, user_id):
    try:
        invite_link = f"https://t.me/{BOT_USERNAME}?start={user_id}"
        update.message.reply_text(f"برای دعوت از دوستان خود از لینک زیر استفاده کنید:\n{invite_link}")

    except Exception as e:

        error_message = f"Error sending invite link to {user_id}: {str(e)}"
        send_error_to_admin(error_message)





def add_invite(inviter_user_id, invitee_user_id):
    try:
        with sqlite3.connect("database.db") as conn:
            c = conn.cursor()
            c.execute('''
            INSERT INTO invites (inviter_user_id, invitee_user_id, used)
            VALUES (?, ?, ?)
            ''', (inviter_user_id, invitee_user_id, False))
            conn.commit()
    except Exception as e:
        error_message = f"Error adding invite for {inviter_user_id} and {invitee_user_id}: {str(e)}"
        send_error_to_admin(error_message)






def check_invite(user_id):
    try:
        with sqlite3.connect("database.db") as conn:
            c = conn.cursor()
            c.execute('SELECT * FROM invites WHERE invitee_user_id = ? AND used = FALSE', (user_id,))
            invite = c.fetchone()
            return invite is not None
    except Exception as e:
        error_message = f"Error checking invite for {user_id}: {str(e)}"
        send_error_to_admin(error_message)
        return False





def use_invite(user_id):
    try:
        with sqlite3.connect("database.db") as conn:
            c = conn.cursor()
            c.execute('UPDATE invites SET used = TRUE WHERE invitee_user_id = ?', (user_id,))
            conn.commit()
    except Exception as e:
        error_message = f"Error updating invite usage for {user_id}: {str(e)}"
        send_error_to_admin(error_message)





async def summarize_article_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.message.from_user.id
    try:
        if check_invite(user_id):
            use_invite(user_id)
            context.user_data["awaiting_ai"] = True
            await update.message.reply_text("لطفاً مقاله خود را ارسال کنید تا آن را خلاصه کنیم.")
        else:
            await update.message.reply_text("شما قبلاً از این قابلیت استفاده کرده‌اید. لطفاً یک نفر را دعوت کنید تا دوباره از آن استفاده کنید.")
            send_invite_link(update,user_id)




    except Exception as e:
 
        error_message = f"Error sending invite link to {user_id}: {str(e)}"
        send_error_to_admin(error_message)
