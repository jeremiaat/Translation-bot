import os
import logging
from flask import Flask, request
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters, ContextTypes
from deep_translator import GoogleTranslator
from dotenv import load_dotenv

# Load environment variables from .env file for local development
# and configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)
load_dotenv()

BOT_TOKEN = os.getenv("BOT_TOKEN")
VERCEL_URL = os.getenv("VERCEL_URL")

# --- Bot and Flask App Initialization ---
if not BOT_TOKEN:
    raise ValueError("BOT_TOKEN environment variable not set.")

# Initialize the bot application
application = ApplicationBuilder().token(BOT_TOKEN).build()

# Initialize Flask app
app = Flask(__name__)

# --- Bot Handlers ---
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Hi! Send me a message and I'll translate it to English.")

async def translate_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    original_text = update.message.text
    logger.info(f"Received text to translate: {original_text}")
    try:
        translated_text = GoogleTranslator(source='auto', target='en').translate(original_text)
        await update.message.reply_text(f'Translated:\n{translated_text}')
    except Exception as e:
        logger.error(f"Translation failed: {e}")
        await update.message.reply_text("Sorry, I couldn't translate that.")

# Add handlers to the application
application.add_handler(CommandHandler('start', start))
application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, translate_message))

# --- Flask Routes ---
@app.route('/')
def index():
    return 'Bot is alive!', 200

@app.route('/api/index', methods=['POST'])
async def webhook():
    """Webhook endpoint to process Telegram updates."""
    try:
        if not application.initialized:
            await application.initialize()
        update = Update.de_json(request.get_json(force=True), application.bot)
        await application.process_update(update)
        return 'ok', 200
    except Exception as e:
        logger.error(f"Error processing update: {e}")
        return 'error', 500

@app.route('/set_webhook', methods=['GET'])
async def set_webhook():
    """Sets the webhook for the bot."""
    if not VERCEL_URL:
        return "VERCEL_URL not configured.", 500
    
    if not application.initialized:
        await application.initialize()

    webhook_url = f"https://{VERCEL_URL}/api/index"
    await application.bot.set_webhook(url=webhook_url, allowed_updates=Update.ALL_TYPES)
    return f"Webhook set to {webhook_url}", 200
