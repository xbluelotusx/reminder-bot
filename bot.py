import os # required for insert tokens and define port
import requests # gives access to APIs, enablesHTTP requests (such as GET, POST, PUT, DELETE) 
from flask import Flask, request #Flask is needed for web app. request is needed to parse the messages (Telegram) and push it as JSON in (Airtable)
from telegram import Bot, Update #Telegram API and Update Object in Telgream
from telegram.ext import Dispatcher, MessageHandler, Filters # The dispatcher will process incoming updates. The message handler will call your handle_message function for any text message that is not a command.

TELEGRAM_TOKEN = os.environ['TELEGRAM_TOKEN']

app = Flask(__name__) #defining app in Flask
bot = Bot(token=TELEGRAM_TOKEN) #creates a bot object

    
def handle_message(update, context):
    user = update.message.from_user
    update.message.reply_text("Your message has been saved!")

@app.route(f"/{TELEGRAM_TOKEN}", methods=["POST"])
def webhook():
    update = Update.de_json(request.get_json(force=True), bot)
    dispatcher.process_update(update)
    return "ok"

dispatcher = Dispatcher(bot, None, workers=0)
dispatcher.add_handler(MessageHandler(Filters.text & ~Filters.command, handle_message))

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)

