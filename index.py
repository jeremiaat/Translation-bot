import os
import asyncio
from flask import Flask, request
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters, ContextTypes
from deep_translator import GoogleTranslator
from dotenv import load_dotenv

# Load environment variables from .env file for local development
load_dotenv()

BOT_TOKEN = os.getenv("BOT_TOKEN")
VERCEL_URL = os.getenv("VERCEL_URL")

# Initialize Flask app
app = Flask(__name__)

# Bot handlers
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Hi! Send me a message in any language and I'll translate it to English.")

async def translate_message(update:Update, context: ContextTypes.DEFAULT_TYPE):
    original_text = update.message.text
    try:
        translated_text = GoogleTranslator(source='auto', target='en').translate(original_text)
        await update.message.reply_text(f'Translated:\n {translated_text}')
    except Exception as e:
        await update.message.reply_text("Sorry, I couldn't translate")

# Build the bot application
application = ApplicationBuilder().token(BOT_TOKEN).build()
application.add_handler(CommandHandler('start',start))
application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, translate_message))

# This runs once when the serverless function starts
if VERCEL_URL:
    asyncio.run(application.bot.set_webhook(f"{VERCEL_URL}/api/index"))

# This is the main entry point for Vercel
@app.route('/api/index', methods=['POST'])
def webhook():
    # Process the update from Telegram
    update = Update.de_json(request.get_json(force=True), application.bot)
    asyncio.run(application.process_update(update))
    return 'ok'