
from telegram import Update, ReplyKeyboardMarkup, KeyboardButton,InlineKeyboardButton,InlineKeyboardMarkup
from telegram.ext import (Application, CommandHandler, MessageHandler, filters, ContextTypes ,
                           CallbackQueryHandler ,PreCheckoutQueryHandler,ConversationHandler)

from telegram.ext import Application, CommandHandler, MessageHandler, filters
import asyncio
import schedule
from threading import Thread
from datetime import datetime
import sqlite3
import random
import os
import string
from dotenv import load_dotenv
import logging
import referral as rs
import course
from tools import *
import wallet_tracker
from config import ADMIN_CHAT_ID,BOT_USERNAME
from twitter import (update_task_step,get_task_step,add_points,start_post,user_state,send_post,get_latest_link,
                      error_handler,handle_twitter_id)

from database import setup_database
from user_handler import contact_us_handler,receive_user_message_handler
from admin_panel import list_courses,receive_admin_response_handler,grant_vip_command,revoke_vip_command,list_vip

from star_pay import (send_invoice,precheckout_callback,successful_payment_callback,
                      send_renewal_notification, send_vip_expired_notification,star_payment_online,star_payment_package)






# from payment import check_payment_status,start_payment
# from database import get_wallets_from_db
# from wallet_tracker import monitor_wallet

BOT_TOKEN = '7378110308:AAFZiP9M5VDiTG5nOqfpgSq3wlrli1bw6NI'





logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s',level=logging.INFO)
logger = logging.getLogger(__name__)

load_dotenv()
token=os.getenv('Token')

conn = sqlite3.connect('Database.db', check_same_thread=False)
c = conn.cursor()





main_menu = [
    [KeyboardButton("معرفی خدمات")],
    [KeyboardButton("🎓 آموزش و کلاس‌های آنلاین")],
    [KeyboardButton("🌟 خدمات VIP"),KeyboardButton("🛠ابزارها")],
    [KeyboardButton("💼 مشاهده امتیاز"),KeyboardButton("📣 دعوت دوستان")],
    [KeyboardButton("ارتباط با ما")]
]



# تابع شروع و 
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_first_name = update.effective_user.first_name
    chat_id = update.effective_chat.id  
    user_id = update.message.from_user.id
    username = update.effective_user.username
    print(f'USER : {username}    ID : {user_id}')
    await save_user(user_id, username, chat_id)

    if not rs.user_exists(user_id):
        rs.register_user(user_id) 

        args = context.args
        if args:
            inviter_id = args[0]  # آی‌دی کاربر دعوت‌کننده را از پارامتر start بگیریم
            if inviter_id.isdigit() and rs.user_exists(int(inviter_id)) and int(inviter_id) != user_id:
                inviter_id = int(inviter_id)

                # بررسی اینکه آیا دعوت تکراری نیست
                if not rs.is_already_referred(inviter_id, user_id):
                    rs.add_points(inviter_id, 10)  # افزایش امتیاز کاربر دعوت‌کننده
                    rs.record_referral(inviter_id, user_id)  # ثبت دعوت در دیتابیس
                    await context.bot.send_message(chat_id=inviter_id, text="🎉 شما 10 امتیاز بابت دعوت کاربر جدید دریافت کردید!")

    welcome_text =f"سلام {user_first_name}! خوش آمدید به ربات ما."
    await update.message.reply_text(welcome_text, reply_markup=ReplyKeyboardMarkup(main_menu, resize_keyboard=True))






async def back_main(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    if query:
        reply_markup = ReplyKeyboardMarkup(main_menu, resize_keyboard=True)
        await query.edit_message_reply_markup(reply_markup=reply_markup)
    else:
        chat_id = update.effective_chat.id
        await context.bot.send_message(chat_id=chat_id, text="لطفاً یکی از گزینه‌های اصلی را انتخاب کنید:", reply_markup=ReplyKeyboardMarkup(main_menu, resize_keyboard=True))



async def save_user(user_id,username,chat_id):
    connection = sqlite3.connect('Database.db')
    cursor = connection.cursor()
    
    cursor.execute('INSERT OR REPLACE INTO users (user_id, username,chat_id) VALUES (?, ?,?)', (user_id, username,chat_id))
    connection.commit()
    connection.close()






async def show_welcome(update:Update,context:ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("""
🎓 آموزش و کلاس‌های آنلاین  
دوره‌های آموزشی تخصصی برای یادگیری ترید میم‌کوین‌ها با محتوای پیشرفته و تجربیات کاربردی. کلاس‌ها هر دو هفته یک‌بار در روزهای پنجشنبه، جمعه یا شنبه با ظرفیت محدود ۵ تا ۱۰ نفر برگزار می‌شود. برای ثبت‌نام، مبلغ را واریز کنید و لینک گروه آموزشی دریافت کنید. در صورت عدم برگزاری کلاس، هزینه به‌طور کامل بازگردانده خواهد شد.

🌟 خدمات VIP  
کانال VIP ما با ارائه سیگنال‌های دقیق و تحلیل‌های تخصصی، فضای مناسبی برای کسب سود در دنیای ترید ایجاد می‌کند. 

 برای سوالات عمومی:  
- کانال عمومی: @memeland_persia  
- گروه عمومی: @memeland_persiaa  

🛠 معرفی ابزارهای ضروری  
ابزارهای موردنیاز برای فعالیت در بلاکچین، شامل دسته‌بندی‌هایی همچون تحلیل چارت‌ها، صرافی‌های غیرمتمرکز و کیف‌پول‌ها، معرفی شده‌اند.

💰 کیف‌پول‌های برتر با Win Rate بالا  
لیستی از کیف‌پول‌هایی با نرخ موفقیت بالا که به‌صورت فایل اکسل و پس از پرداخت قابل دریافت هستند.

📣 دعوت دوستان  
با دریافت لینک دعوت اختصاصی خود، دوستان را به ربات دعوت کرده و امتیازهای ویژه دریافت کنید.
""")



async def show_vip_services(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    user_id = update.message.from_user.id
    chat_id = update.message.chat_id

    try:
        c.execute("SELECT vip_expiry_date FROM vip_users WHERE user_id = ?", (user_id,))
        result = c.fetchone()

        if result:
            
            expiry_date_str = result[0]
            print(expiry_date_str)
            expiry_date = datetime.strptime(expiry_date_str, '%Y-%m-%d %H:%M:%S')
            print(expiry_date)
            remaining_days = (expiry_date - datetime.now()).days
            print(remaining_days)
            if remaining_days > 0:
                await update.message.reply_text(f"شما عضو VIP هستید و {remaining_days} روز از عضویت شما باقی مانده.")
            else:
                await update.message.reply_text("عضویت VIP شما به پایان رسیده است.")
        else:
            await send_invoice(update, context)  # در صورتی که کاربر عضو VIP نباشد، فاکتور ارسال می‌شود.
    
    except Exception as e:
        await update.message.reply_text(f"خطا در پردازش اطلاعات: {e}")


async def show_tools(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    keyboard = [
        [KeyboardButton("Solana")],
        [KeyboardButton("ETH")],
        [KeyboardButton("Sui")],
        [KeyboardButton("بازگشت به صفحه قبل ⬅️")]]
    reply_markup = ReplyKeyboardMarkup(keyboard,resize_keyboard=True)
    await update.message.reply_text("لطفاً یک شبکه را انتخاب کنید:", reply_markup=reply_markup)



async def show_wallets(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    text = "در این بخش می‌توانید ولت‌های معتبر با Win Rate بالا را مشاهده کنید."
    await update.message.reply_text(text)


async def show_twitter_rating(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    text = "در این بخش می‌توانید پروفایل توییتر خود را متصل کرده و امتیاز کسب کنید."
    await update.message.reply_text(text)



async def show_invite_friends(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    user_id = update.effective_user.id
    referral_link = rs.generate_referral_link(BOT_USERNAME, user_id)

    # ارسال لینک دعوت به همراه توضیحات
    await update.message.reply_text(
        f"این لینک اختصاصی شماست:\n{referral_link}\n\nبا ارسال این لینک به دوستان خود می‌توانید امتیاز دریافت کنید.")





# دریافت کد تخفیف
async def generate_discount_code(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    discount_options = [20,30,35,]
    discount = random.choice(discount_options)
    code = ''.join(random.choices(string.ascii_uppercase + string.digits, k=8))
    c.execute("INSERT INTO discount_codes (code, discount) VALUES (?, ?)", (code, discount))
    conn.commit()
    await update.message.reply_text(f"کد تخفیف شما: {code} - میزان تخفیف: {discount}%")





# تابع نمایش امتیاز کاربر
async def show_user_score(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await rs.show_score(update, context)  # فراخوانی تابع نمایش امتیاز از فایل referral_system

async def callback_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        query = update.callback_query
        data = query.data
        chat_id = update.effective_chat.id

        if data.startswith("reply_to_user"):
            user_id = int(query.data.split("_")[-1])
            print(f"STARTWITH REPLY   USER_ID   : {user_id}")
            context.user_data["reply_to"] = user_id
            await query.message.reply_text("لطفاً پیام خود را برای پاسخ به کاربر وارد کنید.")

        elif data == "buy_video_package":
            await course.buy_video_package(update, context)

        elif data == "online_course":
            await course.register_online_course(update, context)

        elif data == "register_video_package":
            await course.get_user_info_package(update, context)

        elif data == "register_online_course":
            await course.get_user_info_online(update, context)

        elif data == "back":
            keyboard = [
                [InlineKeyboardButton("خرید پکیج ویدئویی", callback_data="buy_video_package")],
                [InlineKeyboardButton("ثبت‌نام دوره آنلاین", callback_data="online_course")],
            ]
            reply_markup = InlineKeyboardMarkup(keyboard)
            await none_step(update, context)
            await query.edit_message_reply_markup(reply_markup=reply_markup)

        elif data == 'send_post':
            await send_post(update, context)

        user_id = query.from_user.id
        step = await get_task_step(user_id)
        link = get_latest_link()
        if query.data == "check_disabled":
            await query.answer("ابتدا روی لینک توییتر کلیک کنید!", show_alert=True)
            keyboard = [
                [InlineKeyboardButton("لینک توییتر", url=link),
                 InlineKeyboardButton("✅ چک کردن", callback_data="check_task")]
            ]
            await query.edit_message_reply_markup(reply_markup=InlineKeyboardMarkup(keyboard))
            context.user_data["twitter_id"] = True
        elif query.data == "check_task":
            if step == 1:
                await query.message.reply_text("لطفاً آیدی توییتر خود را ارسال کنید.")
                context.user_data["twitter_id"] = True
                await update_task_step(user_id, 2)
            elif step == 2:
                await query.message.reply_text("هنوز تسک انجام نشده است. دوباره تلاش کنید.")
                await update_task_step(user_id, 3)
            elif step == 3:
                await query.message.reply_text("تسک تأیید شد. امتیاز به شما اضافه شد!")
                await add_points(user_id, 100)
                await update_task_step(user_id, 1)

        await query.answer()

    except Exception as e:
        # مدیریت خطا
        print(f"Error occurred: {e}")
        await query.answer("متأسفانه خطایی رخ داده است. لطفاً دوباره تلاش کنید.")



async def handle_package_step(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.message.from_user.id
    chat_id =update.effective_chat.id
    course_type = 'video'

    c.execute("SELECT course_id from courses WHERE course_type = ? ORDER BY created_at DESC LIMIT 1",(course_type,))
    last_course = c.fetchone()
    print(f"LAST COURSE   :{last_course}")
    if last_course:
        course_id =last_course[0]
    else:
        print("دوره انلاینی موجود نیست فعلا")


    package_step = context.user_data.get('package')
    if package_step == "GET_NAME":
        context.user_data['name_pack'] = update.message.text
        context.user_data['package'] = "GET_EMAIL"
        await update.message.reply_text("لطفاً ایمیل خود را وارد کنید:")

    elif package_step == "GET_EMAIL":
        context.user_data['email_pack'] = update.message.text
        context.user_data['package'] = "GET_PHONE"
        await update.message.reply_text("لطفاً شماره تلفن خود را وارد کنید:")

    elif package_step == "GET_PHONE":
        context.user_data['phone_pack'] = update.message.text
        await course.save_user_info(
            update.effective_user.id,
            update.effective_chat.id,
            context.user_data['name_pack'],
            context.user_data['email_pack'],
            context.user_data['phone_pack']
        )

        # await update.message.reply_text("اطلاعات شما با موفقیت ذخیره شد.")
        
        await star_payment_package(update,context,user_id,course_id)
        context.user_data['package'] = None



async def handle_online_step(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.message.from_user.id
    chat_id =update.effective_chat.id
    course_type = 'online'

    c.execute("SELECT course_id from courses WHERE course_type = ? ORDER BY created_at DESC LIMIT 1",(course_type,))
    last_course = c.fetchone()
    print(f"LAST COURSE   :{last_course}")
    if last_course:
        course_id =last_course[0]
    else:
        print("دوره انلاینی موجود نیست فعلا")
    print(f"COURSE ID   :{course_id}")
    online_step = context.user_data.get('online')
    if online_step == "GET_NAME":
        context.user_data['name_online'] = update.message.text
        context.user_data['online'] = "GET_EMAIL"
        await update.message.reply_text("لطفاً ایمیل خود را وارد کنید:")

    elif online_step == "GET_EMAIL":
        context.user_data['email_online'] = update.message.text
        context.user_data['online'] = "GET_PHONE"
        await update.message.reply_text("لطفاً شماره تلفن خود را وارد کنید:")

    elif online_step == "GET_PHONE":
        context.user_data['phone_online'] = update.message.text
        await course.save_user_info(
            user_id,
            chat_id,
            context.user_data['name_online'],
            context.user_data['email_online'],
            context.user_data['phone_online']
        )
        await star_payment_online(update,context,user_id,course_id)
        # await update.message.reply_text("اطلاعات شما با موفقیت ذخیره شد.")
        context.user_data['online'] = None
        




async def handle_add_course_step(update: Update, user_id: int, text: str):
    if current_step.get(user_id) == "course_name":
        course_data[user_id]["course_name"] = text
        current_step[user_id] = "description"
        await update.message.reply_text("لطفاً توضیحات دوره را وارد کنید:")

    elif current_step.get(user_id) == "description":
        course_data[user_id]["description"] = text
        current_step[user_id] = "price"
        await update.message.reply_text("لطفاً قیمت دوره را وارد کنید:")

    elif current_step.get(user_id) == "price":
        try:
            course_data[user_id]["price"] = float(text)
            current_step[user_id] = "type"
            await update.message.reply_text("لطفاً نوع دوره را وارد کنید:\n\nonline یا video")
        except ValueError:
            await update.message.reply_text("قیمت نامعتبر است! لطفاً یک مقدار عددی وارد کنید:")

    elif current_step.get(user_id) == "type":
        course_data[user_id]["type"] = text

        c.execute(
            "INSERT INTO courses (course_name, description, price, course_type) VALUES (?, ?, ?, ?)",
            (course_data[user_id]["course_name"], 
             course_data[user_id]["description"], 
             course_data[user_id]["price"], 
             course_data[user_id]["type"])
        )
        conn.commit()

        await update.message.reply_text("دوره با موفقیت ثبت شد!")
        course_data.pop(user_id, None)
        current_step.pop(user_id, None)
    




course_data = {}
current_step = {}

# تابع برای شروع دریافت اطلاعات دوره
async def add_courses(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    user_id = update.effective_user.id
    course_data[user_id] = {}
    current_step[user_id] = "course_name"
    await update.message.reply_text("لطفاً نام دوره را وارد کنید:")

async def none_step(update: Update, context: ContextTypes.DEFAULT_TYPE):

    try:
        if update.message:
            user_id = update.message.from_user.id
        elif update.callback_query:
            user_id = update.callback_query.from_user.id
        else:
            raise ValueError("نوع آپدیت مشخص نیست. لطفاً بررسی کنید.")

        # پاک کردن داده‌های مرتبط با کاربر
        context.user_data.pop('online', None)
        context.user_data.pop('package', None)
        context.user_data.pop('stage', None)
        context.user_data.pop('description', None)
        context.user_data.pop('link', None)
        course_data.pop(user_id, None)
        current_step.pop(user_id, None)

        # اطلاع‌رسانی در لاگ یا با print
        print(f"وضعیت و داده‌های کاربر {user_id} با موفقیت پاک شدند.")
    except Exception as e:
        print(f"خطا در پاک‌سازی داده‌های کاربر: {e}")




async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    text = update.message.text
    user_id = update.message.from_user.id
    admin_id = id in ADMIN_CHAT_ID

    command_mapping = {
        "معرفی خدمات": show_welcome,
        "🎓 آموزش و کلاس‌های آنلاین": course.courses_menu,
        "🌟 خدمات VIP": show_vip_services,
        "🛠ابزارها": show_tools,
        "🏆 امتیازدهی توییتر": show_twitter_rating,
        "📣 دعوت دوستان": show_invite_friends,
        "💼 مشاهده امتیاز": show_user_score,
        "ارتباط با ما":contact_us_handler,
        "دریافت کد تخفیف":generate_discount_code,
        "Solana" :Solana_tools,
        "ETH":ETH_tools,
        "Sui":Sui_tools,
        "بازگشت به صفحه قبل ⬅️": back_main
    }
    try:
        if text in command_mapping:
            await none_step(update, context)
            await command_mapping[text](update, context)

        elif update.message.successful_payment:
            await successful_payment_callback(update,context)

        elif text == "مشاهده چارت":
            await view_chart(update, context)
        elif text == "ولت‌های پیشنهادی":
            await recommended_wallets(update, context)
        elif text == "ابزارهای خرید و فروش عادی":
            await basic_trading_tools(update, context)
        elif text == "ابزارهای خرید و فروش حرفه‌ای":
            await advanced_trading_tools(update, context)

        elif text == "افزودن دوره" and str(user_id) in ADMIN_CHAT_ID:
            await add_courses(update, context)

        elif text == "لیست دوره ها" and str(user_id) in ADMIN_CHAT_ID:
            await list_courses(update, context)

        elif context.user_data.get('package'):
            await handle_package_step(update, context)

        elif context.user_data.get('online'):
            await handle_online_step(update, context)

        elif context.user_data.get("awaiting_message"):
            await receive_user_message_handler(update,context)

        elif context.user_data.get("add_wallet"):
            await wallet_tracker.add_wallet(update,context)

        elif context.user_data.get("remove_wallet"):
            await wallet_tracker.remove_wallet(update,context)

        elif "reply_to" in context.user_data:
            await receive_admin_response_handler(update,context)

        elif user_id in current_step:
            await handle_add_course_step(update, user_id, text)

        elif context.user_data.get("twitter_id"):
            await handle_twitter_id(update,context,text)

                    # بررسی وضعیت کاربر و انتقال به مرحله بعد
        elif user_state.get(user_id, {}).get('state') == 'waiting_for_description':
            user_state[user_id]['description'] = update.message.text
            user_state[user_id]['state'] = 'waiting_for_link'
            await update.message.reply_text("توضیحات ذخیره شد. لطفاً لینک توییتر را وارد کنید.")
        elif user_state.get(user_id, {}).get('state') == 'waiting_for_link':
            user_state[user_id]['link'] = update.message.text
            user_state[user_id]['state'] = 'ready_to_send'
            # نمایش دکمه برای تأیید ارسال
            keyboard = [[InlineKeyboardButton("ارسال به کاربران", callback_data="send_post")]]
            reply_markup = InlineKeyboardMarkup(keyboard)
            await update.message.reply_text(
                "توضیحات و لینک ثبت شد. آیا می‌خواهید ارسال کنید؟",
                reply_markup=reply_markup,
            )


    except Exception as e:
        print(f"Error in handle_message: {e}")
        await update.message.reply_text("خطا در پردازش پیام. لطفاً دوباره تلاش کنید.")



import aioschedule as schedule 


async def scheduled_jobs(app):
    """وظایف زمان‌بندی‌شده async"""
    print("Scheduled job is running...")
    await send_renewal_notification(app)
    await send_vip_expired_notification(app)

async def schedule_tasks(app):
    """برنامه‌ریزی و اجرای وظایف زمان‌بندی‌شده"""
    schedule.every().day.at("00:00").do(scheduled_jobs, app=app)
    while True:
        await schedule.run_pending()
        await asyncio.sleep(1)

def run_schedule(app):
    """اجرای حلقه زمان‌بندی وظایف در نخ جداگانه"""
    asyncio.run(schedule_tasks(app))

def main():
    setup_database()
    """راه‌اندازی و اجرای ربات تلگرام"""
    if not BOT_TOKEN:
        raise ValueError("Telegram bot token not found.")

    # تنظیم ربات تلگرام
    app = Application.builder().token(BOT_TOKEN).build()
    app.bot_data['admins'] = [int(id) for id in ADMIN_CHAT_ID]
    # مدیریت دستورات و پیام‌ها
    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    app.add_handler(CommandHandler("add_wallet", wallet_tracker.wait_add_wallet))
    app.add_handler(CommandHandler("remove_wallet", wallet_tracker.wait_remove_wallet))
    app.add_handler(CommandHandler("list_wallets", wallet_tracker.list_wallets))
    app.add_handler(CommandHandler("add_points", rs.add_points_handler))
    app.add_handler(CommandHandler("remove_points", rs.remove_points_handler))
    app.add_handler(CommandHandler("grant_vip", grant_vip_command))
    app.add_handler(CommandHandler("revoke_vip", revoke_vip_command))
    app.add_handler(CommandHandler("list_vip", list_vip))
    app.add_handler(CommandHandler("post", start_post))
    app.add_handler(PreCheckoutQueryHandler(precheckout_callback))
    app.add_handler(CallbackQueryHandler(callback_handler))
    app.add_error_handler(error_handler)

    # اجرای زمان‌بندی در یک نخ جداگانه
    schedule_thread = Thread(target=run_schedule, args=(app,), daemon=True)
    schedule_thread.start()

    # اجرای ربات تلگرام
    app.run_polling()


if __name__ == "__main__":
    main()


