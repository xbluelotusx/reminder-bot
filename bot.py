import os
import requests
from datetime import datetime, time as dtime
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes
from apscheduler.schedulers.background import BackgroundScheduler

TOKEN = os.environ['TELEGRAM_TOKEN']
DATA_FILE = "messages.json"
SEND_HOUR = 18  # 24-hour format. Change to your preferred hour.
SEND_MINUTE = 0  # Change to your preferred minute.

def load_messages():
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, "r") as f:
            return json.load(f)
    return {}

def save_messages(data):
    with open(DATA_FILE, "w") as f:
        json.dump(data, f)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Send me anything and I'll remember it! Every day at the set time, I'll send you everything you've sent me.")

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = str(update.message.from_user.id)
    text = update.message.text

    data = load_messages()
    if user_id not in data:
        data[user_id] = []
    data[user_id].append({"text": text, "timestamp": datetime.now().isoformat()})
    save_messages(data)
    await update.message.reply_text("Got it! I'll remember this.")

async def send_daily(context: ContextTypes.DEFAULT_TYPE):
    data = load_messages()
    for user_id, messages in data.items():
        chat_id = int(user_id)
        history = "\n".join([msg["text"] for msg in messages])
        if history:
            await context.bot.send_message(chat_id=chat_id, text="Your message history:\n" + history)

def schedule_daily_job(application):
    scheduler = BackgroundScheduler(timezone="UTC")
    scheduler.add_job(
        lambda: application.create_task(send_daily(application.bot)),
        trigger="cron",
        hour=SEND_HOUR,
        minute=SEND_MINUTE,
    )
    scheduler.start()

def main():
    application = Application.builder().token(TOKEN).build()
    application.add_handler(CommandHandler("start", start))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    # Start the scheduler after the application has started
    application.post_init = lambda _: schedule_daily_job(application)
    application.run_polling()

if __name__ == "__main__":
    main()
