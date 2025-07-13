import os
import json
from datetime import datetime
from telegram import Update
from telegram.ext import (
    Application,
    CommandHandler,
    MessageHandler,
    ContextTypes,
    filters,
)
from apscheduler.schedulers.background import BackgroundScheduler

# --- CONFIGURATION ---
TOKEN = os.getenv("TELEGRAM_TOKEN")  # Use TELEGRAM_TOKEN from environment
DATA_FILE = "messages.json"
SEND_HOUR = 18     # UTC hour to send (24h format)
SEND_MINUTE = 0    # UTC minute to send

# --- DATA STORAGE ---
def load_messages():
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, "r") as f:
            return json.load(f)
    return {}

def save_messages(data):
    with open(DATA_FILE, "w") as f:
        json.dump(data, f)

# --- HANDLERS ---
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "Send me anything and I'll remember it! Every day at the set time, I'll send you everything you've sent me."
    )

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = str(update.message.from_user.id)
    text = update.message.text

    data = load_messages()
    if user_id not in data:
        data[user_id] = []
    data[user_id].append({
        "text": text,
        "timestamp": datetime.utcnow().isoformat()
    })
    save_messages(data)
    await update.message.reply_text("Got it! I'll remember this.")

async def send_daily(application: Application):
    data = load_messages()
    for user_id, messages in data.items():
        chat_id = int(user_id)
        if messages:
            history = "\n".join(msg["text"] for msg in messages)
            try:
                await application.bot.send_message(
                    chat_id=chat_id,
                    text="Your message history so far:\n" + history
                )
            except Exception as e:
                print(f"Failed to send to {chat_id}: {e}")

# --- SCHEDULER ---
def schedule_daily_job(application: Application):
    scheduler = BackgroundScheduler(timezone="UTC")
    # Function to call the async send_daily from the scheduler
    def job():
        try:
            application.create_task(send_daily(application))
        except Exception as e:
            print(f"Scheduler job error: {e}")
    scheduler.add_job(
        job,
        trigger="cron",
        hour=SEND_HOUR,
        minute=SEND_MINUTE,
    )
    scheduler.start()

async def post_init(application: Application):
    schedule_daily_job(application)

# --- MAIN BOT SETUP ---
def main():
    if not TOKEN:
        print("Please set your Telegram bot token in the TELEGRAM_TOKEN environment variable (Render dashboard).")
        return

    application = Application.builder().token(TOKEN).build()
    application.add_handler(CommandHandler("start", start))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    application.post_init = post_init
    application.run_polling()

if __name__ == "__main__":
    main()
