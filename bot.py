import os
import logging
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters, ContextTypes

TOKEN = os.getenv("BOT_TOKEN", "")

logging.basicConfig(format='%(asctime)s - %(levelname)s - %(message)s', level=logging.INFO)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "🧮 Calculator Bot မှ ကြိုဆိုပါတယ်!\n\n"
        "တွက်ချက်ချင်တာ ရိုက်ထည့်ပါ:\n"
        "➕ ပေါင်း: 5+3\n"
        "➖ နုတ်: 10-4\n"
        "✖️ မြှောက်: 6*7\n"
        "➗ စား: 100/5\n"
        "🔢 ရောပြီးတွက်: (5+3)*2\n\n"
        "ဥပမာ: 1500*3+500"
    )

async def calculate(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text.strip()
    
    # Only allow safe characters for calculation
    allowed = set('0123456789+-*/.() ')
    if not all(c in allowed for c in text):
        await update.message.reply_text("❌ တွက်လို့မရပါ။\nဂဏန်းနဲ့ +, -, *, / ပဲ သုံးပါ။\nဥပမာ: 5+3 သို့ 100*2")
        return
    
    try:
        result = eval(text)
        if isinstance(result, float):
            if result == int(result):
                result = int(result)
            else:
                result = round(result, 2)
        await update.message.reply_text(f"🧮 {text} = {result}")
    except ZeroDivisionError:
        await update.message.reply_text("❌ သုညနဲ့ စားလို့ မရပါ။")
    except:
        await update.message.reply_text("❌ တွက်လို့မရပါ။\nဥပမာ: 5+3 သို့ 100*2")

if __name__ == '__main__':
    app = ApplicationBuilder().token(TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, calculate))
    print("Calculator Bot is running...")
    app.run_polling()
