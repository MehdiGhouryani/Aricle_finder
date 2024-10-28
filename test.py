
اتصال به دیتابیس SQLite

# ایجاد جدول‌ها
cursor.execute('''CREATE TABLE IF NOT EXISTS article_subscribers (chat_id INTEGER PRIMARY KEY)''')
cursor.execute('''CREATE TABLE IF NOT EXISTS news_subscribers (chat_id INTEGER PRIMARY KEY)''')
conn.commit()

ذخیره شناسه کاربر در دیتابیس
def add_subscriber(chat_id, table):
    conn = sqlite3.connect('subscribers.db')
    cursor = conn.cursor()

    cursor.execute(f'INSERT OR IGNORE INTO {table} (chat_id) VALUES (?)', (chat_id,))
    conn.commit()
    conn.close()
# حذف شناسه کاربر از دیتابیس


def remove_subscriber(chat_id, table):
    conn = sqlite3.connect('subscribers.db')
    cursor = conn.cursor()

    cursor.execute(f'DELETE FROM {table} WHERE chat_id = ?', (chat_id,))
    conn.commit()
    conn.close()


# واکشی تمام مشترکین
def get_subscribers(table):
    conn = sqlite3.connect('subscribers.db')
    cursor = conn.cursor()

    try:
        cursor.execute(f'SELECT chat_id FROM {table}')
    
        subscribers=[row[0] for row in cursor.fetchall()]
    finally:
        conn.close()
    
    return subscribers

# لیست کلیدواژه‌های مقالات مهندسی پزشکی
keywords_article = [

    "Biomaterials", "Bioinformatics", "Biomedical Imaging", "Biomimetics", 
    "Tissue Engineering", "Medical Devices", "Neuroengineering", "Biosensors", 
    "Bioprinting", "Clinical Engineering", "Rehabilitation Engineering", 
    "Bioelectrics", "Biomechanics", "Nanomedicine", "Regenerative Medicine", 
    "Biomedical Signal Processing", "Medical Robotics", "Wearable Health Technology", 
    "Telemedicine", "Cardiovascular Engineering", "Orthopaedic Bioengineering", 
    "Prosthetics and Implants", "Artificial Organs", "Cancer Bioengineering", 
    "Biomedical Data Science", "Biophotonics", "Medical Imaging Informatics", 
    "Robotic Surgery", "Wearable Sensors", "Digital Health", "Biomedical Optics", 
    "Point-of-Care Diagnostics", "Cardiac Engineering", "Personalized Medicine", 
    "Gene Therapy"

]

TARGET = '@Articles_studentsBme'  # کانال آرشیو مقالات

# تابع ارسال مقاله به کاربران
async def send_article(context: CallbackContext):
    selected_keyword = random.choice(keywords_article)
    search_query = scholarly.search_pubs(selected_keyword)
    articles = [next(search_query) for _ in range(5)]
    random_article = random.choice(articles)



    abstract = random_article['bib'].get('abstract', 'No abstract available')

    result = f"📚 {random_article['bib']['title']}\n" \
             f"👨‍🔬 Author(s): {', '.join(random_article['bib']['author'])}\n" \
             f"📅 Year: {random_article['bib'].get('pub_year', 'Unknown')}\n" \
             f"🔗 [Link to Article]({random_article.get('pub_url', '#')})\n\n\n" \
             f"Abstract:\n{abstract}\n\n" \
                "--"

    try:
        # ارسال به کاربران
        subscribers = get_subscribers('article_subscribers')
        for user_id in subscribers:
            await context.bot.send_message(chat_id=user_id, text=result, parse_mode=ParseMode.MARKDOWN, disable_web_page_preview=True)

        # ارسال به کانال آرشیو
        await context.bot.send_message(chat_id=TARGET, text=result, parse_mode=ParseMode.MARKDOWN, disable_web_page_preview=True)
    
    except Exception as e:
        print(f"ERROR : {e}")


    try:
        genai.configure(api_key=gen_token)

        model = genai.GenerativeModel("gemini-1.5-flash")
        content = f"""لطفا این مقاله رو به شکل خیلی خوب و با جزيیات بررسی کن و برداشت هات رو به شکل زبان عامیانه فارسی به‌طور کامل شرح بده بطور علمی و دقیق با فرمولها و دلایل حرفه‌ای و دقیقا توضیح بده این مقاله رو.

لینک مقاله و خلاصه‌ای ازش: {result}
دقت کن حدود 8 تا 12 خط باشه توضیحاتت
لطفا انتهای پست هم رفرنس بزار 
"""
        response = await model.generate_content(content)
        text_ai = response.replace("#", "")

        subscribers = get_subscribers('article_subscribers')
        for user_id in subscribers:
            await context.bot.send_message(chat_id=user_id, text=text_ai, parse_mode=ParseMode.MARKDOWN, disable_web_page_preview=True)

        # ارسال به کانال آرشیو
        await context.bot.send_message(chat_id=TARGET, text=text_ai, parse_mode=ParseMode.MARKDOWN, disable_web_page_preview=True)
    



    except Exception as e:
        print(f"ERROR : {e}")





# عضویت در بخش مقالات
async def subscribe(update: Update, context: CallbackContext):
    user_id = update.effective_user.id
    
    add_subscriber(user_id, 'article_subscribers')
    context.job_queue.run_repeating(send_article, interval=10000, first=0)  
    await update.message.reply_text("شما با موفقیت عضو بخش مقالات مهندسی پزشکی شدید ✅")

# لغو عضویت در بخش مقالات
async def unsubscribe(update: Update, context: CallbackContext):
    user_id = update.effective_user.id

    remove_subscriber(user_id, 'article_subscribers')
    await update.message.reply_text("عضویت شما لغو شد. دیگر مقالاتی دریافت نخواهید کرد.")



