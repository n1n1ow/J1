import subprocess
import sys

required = ["python-telegram-bot==20.3", "requests"]
for pkg in required:
    try:
        __import__(pkg.split("==")[0])
    except ImportError:
        subprocess.check_call([sys.executable, "-m", "pip", "install", pkg])

import logging
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes, CallbackQueryHandler
import requests, random, string

BOT_TOKEN = "YOUR_BOT_TOKEN_HERE"
AUTHORIZED_CHAT_ID = 5068844201

logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_chat.id != AUTHORIZED_CHAT_ID:
        return
    await update.message.reply_text(
        "👋 أهلاً بك في Insta J Bot!\n"
        "🧪 /check @username — لفحص يوزر\n"
        "⚙️ /generate — لتوليد يوزرات تلقائيًا\n"
        "📦 يعمل على Windows 10"
    )

async def check(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_chat.id != AUTHORIZED_CHAT_ID:
        return
    if not context.args:
        return await update.message.reply_text("❗️ أرسل /check @username")
    user = context.args[0].lstrip("@")
    url = f"https://www.instagram.com/{user}/"
    try:
        res = requests.get(url, timeout=10)
        text = f"✅ @{user} متاح!" if res.status_code == 404 else f"❌ @{user} غير متاح!"
    except Exception as e:
        text = f"⚠️ خطأ أثناء الفحص: {e}"
    buttons = [[
        InlineKeyboardButton("🔁 إعادة الفحص", callback_data=f"recheck_{user}"),
        InlineKeyboardButton("📋 نسخ", callback_data=f"copy_{user}")
    ]]
    await update.message.reply_text(text, reply_markup=InlineKeyboardMarkup(buttons))

async def button_cb(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_chat.id != AUTHORIZED_CHAT_ID:
        return
    query = update.callback_query
    await query.answer()
    data = query.data
    user = data.split("_", 1)[1]
    if data.startswith("recheck_"):
        url = f"https://www.instagram.com/{user}/"
        res = requests.get(url)
        text = f"✅ @{user} متاح!" if res.status_code == 404 else f"❌ @{user} غير متاح!"
        await query.message.reply_text(f"🔁 نتيجة الفحص: {text}")
    elif data.startswith("copy_"):
        await query.message.reply_text(f"📋 @{user}")

def generate_usernames(style="random", count=10):
    usernames = []
    for _ in range(count):
        if style == "three":
            u = ''.join(random.choices(string.ascii_lowercase + string.digits, k=3))
        elif style == "word":
            word = random.choice(["king", "dark", "insta", "pro", "snap", "ghost", "user", "free"])
            num = ''.join(random.choices(string.digits, k=2))
            u = word + num
        else:
            length = random.randint(5, 7)
            u = ''.join(random.choices(string.ascii_lowercase + string.digits, k=length))
        usernames.append(u)
    return usernames

async def generate(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_chat.id != AUTHORIZED_CHAT_ID:
        return
    await update.message.reply_text("⚙️ جاري توليد اليوزرات...")
    style = context.args[0] if context.args else "random"
    count = int(context.args[1]) if len(context.args) > 1 else 10
    results = generate_usernames(style, count)

    for u in results:
        url = f"https://www.instagram.com/{u}/"
        try:
            res = requests.get(url, timeout=10)
            text = f"✅ @{u} متاح!" if res.status_code == 404 else f"❌ @{u} غير متاح!"
        except:
            text = "⚠️ خطأ أثناء الفحص"
        buttons = [[
            InlineKeyboardButton(f"🔍 إعادة الفحص", callback_data=f"recheck_{u}"),
            InlineKeyboardButton("📋 نسخ", callback_data=f"copy_{u}")
        ]]
        await update.message.reply_text(f"{text}", reply_markup=InlineKeyboardMarkup(buttons))

def main():
    app = ApplicationBuilder().token(BOT_TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("check", check))
    app.add_handler(CommandHandler("generate", generate))
    app.add_handler(CallbackQueryHandler(button_cb))
    app.run_polling()

if __name__ == "__main__":
    main()