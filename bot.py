import os
import re
import json
import logging
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters, ContextTypes

TOKEN = os.getenv("BOT_TOKEN", "")
ADMIN_ID = int(os.getenv("ADMIN_ID", "1127663898"))
USERS_FILE = "users.json"

logging.basicConfig(format='%(asctime)s - %(levelname)s - %(message)s', level=logging.INFO)

# Pattern to match math expressions only (must contain at least one operator)
MATH_PATTERN = re.compile(r'^[\d\s\+\-\*\/\.\(\)]+$')
HAS_OPERATOR = re.compile(r'[\+\-\*\/]')

def load_users():
    try:
        with open(USERS_FILE, "r") as f:
            return json.load(f)
    except:
        return {}

def save_users(users):
    with open(USERS_FILE, "w") as f:
        json.dump(users, f)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    
    # Save user
    users = load_users()
    is_new = str(user.id) not in users
    users[str(user.id)] = {
        "name": user.full_name,
        "username": user.username or ""
    }
    save_users(users)
    
    await update.message.reply_text(
        "⚡ Just type the numbers. I'll handle the rest.\n\n"
        "🧮  5+3  |  100*2  |  (50+50)/4"
    )
    
    # Notify admin about new user
    if is_new:
        try:
            username = f"@{user.username}" if user.username else "No username"
            notify_text = (
                f"👤 New User!\n"
                f"Name: {user.full_name}\n"
                f"Username: {username}\n"
                f"ID: {user.id}\n"
                f"Total Users: {len(users)}"
            )
            await context.bot.send_message(chat_id=ADMIN_ID, text=notify_text)
        except Exception as e:
            logging.error(f"Failed to notify admin: {e}")

async def calculate(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text.strip()
    
    # Only respond if it looks like a math expression
    # Must match math pattern AND contain at least one operator
    if not MATH_PATTERN.match(text) or not HAS_OPERATOR.search(text):
        return  # Silently ignore non-math messages
    
    try:
        result = eval(text)
        if isinstance(result, float):
            if result == int(result):
                result = int(result)
            else:
                result = round(result, 2)
        await update.message.reply_text(f"🧮 {text} = {result}")
    except ZeroDivisionError:
        await update.message.reply_text("❌ Cannot divide by zero.")
    except:
        pass  # Silently ignore invalid expressions

async def users(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id != ADMIN_ID:
        return
    all_users = load_users()
    await update.message.reply_text(f"📊 Total Users: {len(all_users)}")

if __name__ == '__main__':
    app = ApplicationBuilder().token(TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("users", users))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, calculate))
    print("Calculator Bot is running...")
    app.run_polling()
