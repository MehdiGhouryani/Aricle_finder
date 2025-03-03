import sqlite3
from config import send_error_to_admin
DB_PATH = 'database.db'

def init_db():
    conn = sqlite3.connect(DB_PATH, check_same_thread=False)
    cursor = conn.cursor()

    cursor.execute('''CREATE TABLE IF NOT EXISTS stats (searches_successful INTEGER, searches_failed INTEGER)''')
    cursor.execute('''CREATE TABLE IF NOT EXISTS auto_article (chat_id INTEGER, keywords TEXT)''')

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS points (
            user_id INT REFERENCES users(user_id) PRIMARY KEY,
            score INTEGER NOT NULL DEFAULT 80
)""")
     
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS referrals (
           inviter_id INTEGER,
           invited_id INTEGER,
           UNIQUE(inviter_id,invited_id)
)''')
    
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            user_id INTEGER PRIMARY KEY,
            chat_id INTEGER,
            username TEXT,
            invited_by INTEGER,
            invite_count INTEGER DEFAULT 0,
            last_summary_date DATE,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
)''')

    conn.commit()
    conn.close()



def get_connection():
    return sqlite3.connect(DB_PATH, check_same_thread=False)


async def increment_invite_count(inviter_user_id):
    try:
        conn = sqlite3.connect(DB_PATH)
        c = conn.cursor()
        
        c.execute('''
        UPDATE users
        SET invite_count = invite_count + 1
        WHERE user_id = ?
        ''', (inviter_user_id,))
        
        conn.commit()
        conn.close()
    except Exception as e:
        error_message = f"Error incrementing invite_count for inviter {inviter_user_id}: {str(e)}"
        await send_error_to_admin(error_message)


def save_user_data(user_id, chat_id, username):
    try:
        conn = sqlite3.connect(DB_PATH)
        c = conn.cursor()
        
        c.execute('''
        INSERT OR IGNORE INTO users (user_id, chat_id, username)
        VALUES (?, ?, ?)
        ''', (user_id, chat_id, username))
        
        conn.commit()
        conn.close()
    except Exception as e:
        error_message = f"Error saving user data: {str(e)}"
        print(f"ERROR IN SAVE USER DATA    :{error_message}")
