import os
import logging
from dotenv import load_dotenv
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters, ContextTypes
from agent import process_user_query

# Configure logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)

load_dotenv()
TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
# Make sure to set OPENAI_API_KEY or GEMINI_API_KEY in your .env if using CrewAI with standard LLMs
# e.g. OPENAI_API_KEY="your-api-key"

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
    
    # Send a "typing" indicator or a preliminary message
    await update.message.reply_text("🤔 Analyzing your request...")
    
    try:
        # Pass the query to the CrewAI agent
        response = process_user_query(user_query)
        await update.message.reply_text(response)
    except Exception as e:
        logging.error(f"Error processing query: {e}")
        await update.message.reply_text("Sorry, I encountered an error while processing your request. Please check the logs.")

if __name__ == '__main__':
    if not TELEGRAM_TOKEN:
        print("Error: TELEGRAM_TOKEN not found in environment variables. Please create a .env file.")
        exit(1)
        
    application = ApplicationBuilder().token(TELEGRAM_TOKEN).build()
    
    application.add_handler(CommandHandler("start", start))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    
    print("Bot is starting...")
    application.run_polling()
