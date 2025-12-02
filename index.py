import os
import asyncio
import logging
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

async def main():
    if not BOT_TOKEN:
        logger.error("BOT_TOKEN not configured.")
        return

    application = ApplicationBuilder().token(BOT_TOKEN).build()

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

    # Run the bot
    await application.run_polling()

if __name__ == '__main__':
    asyncio.run(main())
