import os
import asyncio
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

# Initialize Flask app
app = Flask(__name__)

# Add a simple root route to check if the bot is alive
@app.route('/', methods=['GET'])
def home():
    return "Bot is alive and listening.", 200

# Bot handlers
# This is the main entry point for Vercel

@app.route('/api/index', methods=['POST'])
def webhook():
    logger.info("Webhook received!")
    try:
        # Check if BOT_TOKEN is set
        if not BOT_TOKEN:
            logger.error("BOT_TOKEN not configured.")
            return "BOT_TOKEN not configured.", 500

        async def process_update():
            try:
                # Try to build the bot application
                try:
                    application = ApplicationBuilder().token(BOT_TOKEN).build()
                    logger.info("Bot application built successfully.")
                except Exception as e:
                    logger.error(f"Failed to build bot application: {e}")
                    raise

                # Handlers
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

                application.add_handler(CommandHandler('start', start))
                application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, translate_message))

                # Process the update from Telegram
                update = Update.de_json(request.get_json(force=True), application.bot)
                await application.process_update(update)
                logger.info("Update processed successfully.")

            except Exception as e:
                logger.exception("Error during application build or handler registration")
                raise

        asyncio.run(process_update())
        return 'ok'

    except Exception as e:
        logger.exception(f"Error in webhook: {e}")
        return 'error', 500

# A separate route to set the webhook
@app.route('/set_webhook', methods=['GET', 'POST'])
def set_webhook():
    if VERCEL_URL and BOT_TOKEN:
        logger.info("Setting webhook...")
        async def set_webhook_async():
            application = ApplicationBuilder().token(BOT_TOKEN).build()
            await application.bot.set_webhook(f"https://{VERCEL_URL}/api/index", allowed_updates=Update.ALL_TYPES)
        asyncio.run(set_webhook_async())
        return "Webhook has been set."
    return "VERCEL_URL or BOT_TOKEN not configured.", 500
