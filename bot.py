import os
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters, ContextTypes
from deep_translator import GoogleTranslator
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

BOT_TOKEN = os.getenv("BOT_TOKEN")

# /start command handler
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Hi! Send me a message in any language and I'll translate it to English.")

async def translate_message(update:Update, context: ContextTypes.DEFAULT_TYPE):
    original_text = update.message.text

    try:
        translated_text = GoogleTranslator(source='auto', target='en').translate(original_text)
        await update.message.reply_text(f'''Translated:\n {translated_text}''')
    except Exception as e:
        await update.message.reply_text("Sorry, I coudn't translate")


def main():
    application = ApplicationBuilder().token(BOT_TOKEN).build()
    application.add_handler(CommandHandler('start',start))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, translate_message))
    print('bot is running...')
    application.run_polling()


if __name__ == '__main__':
    main()