from telegram import Update
from telegram.ext import ContextTypes
from telegram import ReplyKeyboardMarkup, KeyboardButton,InlineKeyboardButton,InlineKeyboardMarkup

def tools_keyboard():
    keyboard = [
        [KeyboardButton("مشاهده چارت"),KeyboardButton("ولت‌های پیشنهادی")],
        [KeyboardButton("ابزارهای خرید و فروش عادی")],
        [KeyboardButton("ابزارهای خرید و فروش حرفه‌ای")],
        [KeyboardButton("بازگشت به صفحه قبل ⬅️")]
    ]
    return ReplyKeyboardMarkup(keyboard, resize_keyboard=True)


async def view_chart(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [
        [InlineKeyboardButton("مشاهده ویدیو آموزشی", url="https://t.me/memeland_persia/2151")],
        [InlineKeyboardButton("ورود به سایت TradingView", url="https://www.tradingview.com")],
        [InlineKeyboardButton("ورود به سایت SolScan", url="https://solscan.io")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    text = """🔍 **راهنمای مشاهده چارت‌های قیمتی سولانا**

برای مشاهده نمودارهای زنده شبکه سولانا و توکن‌های آن می‌توانید از سایت‌های زیر استفاده کنید:
1. [TradingView](https://www.tradingview.com): ارائه نمودارهای حرفه‌ای برای تحلیل قیمت سولانا و توکن‌های آن.
2. [SolScan](https://solscan.io): یک مرورگر بلاک‌چین برای شبکه سولانا، مناسب برای مشاهده تراکنش‌ها، چارت‌ها و اطلاعات توکن‌های سولانا.

**نحوه جستجو و بررسی توکن‌ها:**
1. توکن یا کانترکت مورد نظر خود را از SolScan یا منابع معتبر سولانا کپی کنید.
2. در سایت TradingView یا SolScan، توکن را جستجو کرده و چارت قیمت و اطلاعات تکمیلی را مشاهده کنید.

💡 **نکات تکمیلی:**
- برای تحلیل دقیق‌تر می‌توانید از اندیکاتورهای موجود در TradingView مانند MACD و RSI استفاده کنید.
- برای آگاهی از آخرین تراکنش‌های شبکه سولانا و بررسی وضعیت تراکنش‌ها، SolScan گزینه مناسبی است.
    """
    await update.message.reply_text(text, reply_markup=reply_markup, parse_mode='Markdown')


async def recommended_wallets(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = """💼 **ولت‌های پیشنهادی برای ذخیره‌سازی سولانا و توکن‌های مرتبط**

برای امنیت بیشتر و مدیریت دارایی‌های سولانا، از ولت‌های زیر می‌توانید استفاده کنید:

1. **Phantom**
   - [دانلود از سایت رسمی](https://phantom.app)
   - یک کیف پول امن، سریع و کاربرپسند برای ذخیره‌سازی SOL و توکن‌های شبکه سولانا. همچنین امکان اتصال به DAppهای سولانا را فراهم می‌کند.

2. **Sollet**
   - [دانلود و اطلاعات بیشتر](https://www.sollet.io)
   - یک کیف پول غیرحضانتی برای شبکه سولانا، مناسب برای کاربران حرفه‌ای.

3. **Solflare**
   - [دانلود از سایت رسمی](https://solflare.com)
   - یک ولت چندکاره که امکان مدیریت دارایی‌ها، شرکت در استیکینگ و ارتباط با DAppهای سولانا را به کاربران می‌دهد.

📹 **آموزش ویدئویی نصب و استفاده از ولت‌های سولانا:**
- می‌توانید ویدئوی آموزشی را از اینجا مشاهده کنید: [آموزش ویدئویی](https://t.me/memeland_persia/2171)
    """
    await update.message.reply_text(text, parse_mode='Markdown')



async def basic_trading_tools(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = """
ابزارهای زیر برای خرید و فروش توکن‌های شبکه سولانا با کارمزد پایین و سادگی بالا مناسب هستند:

1. **Jupiter** 
   - [ورود به پلتفرم Jupiter](https://jup.ag)
   - پلتفرمی برای تبدیل سریع توکن‌ها در شبکه سولانا، با نرخ‌های بهینه و رابط کاربری ساده.

2. **Raydium**
   - [ورود به پلتفرم Raydium](https://raydium.io)
   - بازارسازی خودکار و صرافی غیرمتمرکز با امکاناتی برای تأمین نقدینگی و شرکت در فارمینگ.

📹 **لینک‌های آموزشی و توضیحات بیشتر**: [لینک‌های مربوطه](https://t.me/memeland_persia/2173)
    """
    await update.message.reply_text(text, parse_mode='Markdown')


async def advanced_trading_tools(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [
        [InlineKeyboardButton("لینک ثبت نام در صرافی سولانا", url="https://example.com")],
        [InlineKeyboardButton("راهنمای پیشرفته برای کاربران حرفه‌ای سولانا", url="https://t.me/memeland_persia/2190")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    text = """📊 **ابزارهای خرید و فروش حرفه‌ای برای شبکه سولانا**

اگر به ابزارهای حرفه‌ای برای معاملات پیشرفته در شبکه سولانا نیاز دارید، این موارد را بررسی کنید:

1. **Orca**
   - پلتفرم معاملاتی غیرمتمرکز با سرعت بالا و رابط کاربری پیشرفته. مناسب برای کاربران حرفه‌ای و افرادی که به دنبال بهینه‌سازی معاملات هستند.

2. **Serum**
   - پروتکل دیفای برای مبادله غیرمتمرکز توکن‌های سولانا. مناسب برای کاربران حرفه‌ای که به دنبال کنترل بیشتری در معاملات و بهینه‌سازی کارمزد هستند.

💼 **نکات مهم برای استفاده از ابزارهای حرفه‌ای در شبکه سولانا:**
- قبل از شروع معاملات حرفه‌ای، توصیه می‌شود با مدیریت ریسک‌ها و استفاده از ابزارهای تحلیلی، برنامه‌ریزی دقیق‌تری انجام دهید.
    """
    await update.message.reply_text(text, reply_markup=reply_markup, parse_mode='Markdown')
