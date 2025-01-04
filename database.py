import sqlite3

DB_PATH = 'users.db'

def init_db():
    conn = sqlite3.connect(DB_PATH, check_same_thread=False)
    cursor = conn.cursor()
    cursor.execute('''CREATE TABLE IF NOT EXISTS users (id INTEGER PRIMARY KEY, username TEXT, keywords TEXT, state TEXT)''')
    cursor.execute('''CREATE TABLE IF NOT EXISTS stats (searches_successful INTEGER, searches_failed INTEGER)''')
    cursor.execute('''CREATE TABLE IF NOT EXISTS auto_article (chat_id INTEGER, keywords TEXT)''')
    cursor.execute('INSERT OR IGNORE INTO stats (searches_successful, searches_failed) VALUES (0, 0)')
    conn.commit()
    conn.close()

def get_connection():
    return sqlite3.connect(DB_PATH, check_same_thread=False)
