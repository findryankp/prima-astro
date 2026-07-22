import asyncio
import logging
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters, ContextTypes
from app.config import TELEGRAM_TOKEN
from app.delivery.worker.tasks import process_query_task

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Send a message when the command /start is issued."""
    welcome_message = (
        "Hello! I am your Agentic AI Sparepart Bot. 🤖\n\n"
        "You can ask me things like:\n"
        "- 'Berapa sisa stock PALU KARET?'\n"
        "- 'Tampilkan barang dengan stok menipis'\n"
        "- 'Siapa yang sering ambil KAWAT LAS?'\n"
        "- 'Prediksi kebutuhan OLI SUPER SLIDE bulan depan'\n\n"
        "How can I help you today?"
    )
    await update.message.reply_text(welcome_message)


async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle normal user text messages by passing them to CrewAI."""
    user_query = update.message.text

    await update.message.reply_text("🤔 Analyzing your request...")

    try:
        # Push the query onto the same Celery/Redis queue used by the Web
        # Dashboard, so requests from both surfaces are processed one at a
        # time. .get() is blocking, so run it in a worker thread to avoid
        # freezing the bot's event loop.
        async_result = process_query_task.delay(user_query)
        response = await asyncio.to_thread(async_result.get, 180)
        await update.message.reply_text(response)
    except Exception as e:
        logging.error(f"Error processing query: {e}")
        await update.message.reply_text("Sorry, I encountered an error while processing your request. Please check the logs.")


def run():
    if not TELEGRAM_TOKEN:
        print("Error: TELEGRAM_TOKEN not found in environment variables. Please create a .env file.")
        raise SystemExit(1)

    application = ApplicationBuilder().token(TELEGRAM_TOKEN).build()

    application.add_handler(CommandHandler("start", start))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

    print("Bot is starting...")
    application.run_polling()
