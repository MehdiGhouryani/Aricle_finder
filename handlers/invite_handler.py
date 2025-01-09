from telegram import Bot,Update
from telegram.ext import ContextTypes
from config import BOT_USERNAME,send_error_to_admin
import sqlite3


INITIAL_SCORE = 5000




def user_exists(user_id):
    conn = sqlite3.connect("database.db")
    cursor =conn.cursor()
    cursor.execute("SELECT COUNT(*) FROM points WHERE user_id = ?",(user_id,))
    exists = cursor.fetchone()[0] > 0
    conn.close()
    return exists



# بررسی اینکه آیا کاربر قبلاً توسط دعوت‌کننده دعوت شده است
def is_already_referred(inviter_id, invited_id):
    conn = sqlite3.connect("database.db")
    cursor = conn.cursor()
    cursor.execute("SELECT COUNT(*) FROM referrals WHERE inviter_id = ? AND invited_id = ?", (inviter_id, invited_id))
    already_referred = cursor.fetchone()[0] > 0
    conn.close()
    return already_referred

# ثبت دعوت جدید در دیتابیس
def record_referral(inviter_id, invited_id):
    conn = sqlite3.connect("database.db")
    cursor = conn.cursor()
    cursor.execute("INSERT OR IGNORE INTO referrals (inviter_id, invited_id) VALUES (?, ?)", (inviter_id, invited_id))
    conn.commit()
    conn.close()



def register_user(user_id):
    conn = sqlite3.connect('database.db')
    cursor = conn.cursor()
    cursor.execute("INSERT OR IGNORE INTO points (user_id, score) VALUES (?, ?)", (user_id, INITIAL_SCORE))
    conn.commit()
    conn.close()


def add_points(user_id, points):
    connection = sqlite3.connect("database.db")
    cursor = connection.cursor()
    cursor.execute("INSERT OR IGNORE INTO points (user_id, score) VALUES (?, 0)", (user_id,))
    cursor.execute("UPDATE points SET score = score + ? WHERE user_id = ?", (points, user_id))
    connection.commit()
    connection.close()






async def send_invite_link(update:Update, user_id):
    conn = sqlite3.connect('database.db')
    cursor = conn.cursor()
    cursor.execute("SELECT score FROM points WHERE user_id = ?", (user_id,))
    score = cursor.fetchone()
    conn.close()

    try:
        invite_link = f"https://t.me/{BOT_USERNAME}?start={user_id}"
        await update.message.reply_text(f"""برای دعوت از دوستان خود از لینک زیر استفاده کنید:
{invite_link}

امتیاز فعلی شما : {score[0]}
""")

    except Exception as e:

        error_message = f"Error sending invite link to {user_id}: {str(e)}"
        await send_error_to_admin(error_message)


# تابعی برای نمایش امتیاز کاربر
async def show_score(update: Update):
    user_id = update.effective_user.id
    conn = sqlite3.connect('database.db')
    cursor = conn.cursor()
    cursor.execute("SELECT score FROM points WHERE user_id = ?", (user_id,))
    score = cursor.fetchone()
    conn.close()

    if score:
        await update.message.reply_text(f"امتیاز شما: {score[0]}")
    else:
        await update.message.reply_text("شما هنوز ثبت‌نام نکرده‌اید.")


import sqlite3

# تابع برای بررسی امتیاز کاربر
def check_score(user_id):
    with sqlite3.connect("database.db") as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT score FROM points WHERE user_id = ?", (user_id,))
        score = cursor.fetchone()
        return score and score[0] >= 50  # بررسی امتیاز کافی

# تابع برای کسر 50 امتیاز از کاربر
def use_score(user_id):
    with sqlite3.connect("database.db") as conn:
        cursor = conn.cursor()
        cursor.execute("UPDATE points SET score = score - 50 WHERE user_id = ? AND score >= 50", (user_id,))
        conn.commit()



async def summarize_article_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.message.from_user.id
    try:
        if check_score(user_id):
            use_score(user_id)
            context.user_data["awaiting_ai"] = True
            await update.message.reply_text("لطفاً مقاله خود را ارسال کنید تا آن را خلاصه کنیم.")
        else:
            await update.message.reply_text("مثل اینک امتیازت کافی نیست !")
            await send_invite_link(update,user_id)

    except Exception as e:
 
        error_message = f"summarize_article_handler{user_id}: {str(e)}"
        await send_error_to_admin(error_message)
