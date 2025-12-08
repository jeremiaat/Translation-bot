import os
import logging
import json
import asyncio
from http.server import BaseHTTPRequestHandler, HTTPServer
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters, ContextTypes
from deep_translator import GoogleTranslator
from dotenv import load_dotenv

# --- Setup ---
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)
load_dotenv()

BOT_TOKEN = os.getenv("BOT_TOKEN")

# --- Bot Handlers ---
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Sends a welcome message when the /start command is issued."""
    await update.message.reply_text("Hi! Send me a message and I'll translate it to English.")

async def translate_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Translates the user's message to English."""
    original_text = update.message.text
    logger.info(f"Received text to translate: {original_text}")
    try:
        translated_text = GoogleTranslator(source='auto', target='en').translate(original_text)
        logger.info(f"Translation successful: {translated_text}")
        await update.message.reply_text(f'Translated:\n{translated_text or ""}')
    except Exception as e:
        logger.error(f"Translation failed: {e}")
        await update.message.reply_text("Sorry, I couldn't translate that.")

def add_handlers(application):
    """Adds command and message handlers to the application."""
    application.add_handler(CommandHandler('start', start))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, translate_message))

async def handle_request(body: str):
    """
    Builds the application, processes a single update, and shuts down.
    This is the serverless-friendly approach.
    """
    application = ApplicationBuilder().token(BOT_TOKEN).build()
    add_handlers(application)
    await application.initialize()
    update = Update.de_json(json.loads(body), application.bot)
    await application.process_update(update)
    await application.shutdown()

class handler(BaseHTTPRequestHandler):
    """
    Vercel's entrypoint for serverless functions.
    This handles POST requests from Telegram.
    """
    def do_POST(self):
        if not BOT_TOKEN:
            logger.error("BOT_TOKEN environment variable not set.")
            self.send_response(500)
            self.end_headers()
            self.wfile.write(b"BOT_TOKEN not set.")
            return
            
        try:
            content_length = int(self.headers["Content-Length"])
            body = self.rfile.read(content_length).decode("utf-8")
            asyncio.run(handle_request(body))
            self.send_response(200)
            self.end_headers()
        except Exception as e:
            logger.error(f"Error processing update: {e}")
            self.send_response(500)
            self.end_headers()
            self.wfile.write(f"Error: {e}".encode("utf-8"))
