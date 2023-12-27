import logging
from telegram import Update
from telegram.ext import Application, MessageHandler, filters, ContextTypes

# Enable logging
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    level=logging.INFO)

logger = logging.getLogger(__name__)

# Define a function to handle incoming messages
async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    message = update.message
    # Log the received message
    logger.info(f'Received message: {message.text}')
    # Print the received message to the console
    print(f'Received message: {message.text}')

def main() -> None:
    # Create the Application and pass it your bot's token.
    application = Application.builder().token('6597287234:AAEDgR2GkUUfoaBGg-eI0tWbVqtO8lr_qFQ').build()

    # Register the message handler
    application.add_handler(MessageHandler(filters.TEXT, handle_message))

    # Run the bot until the user presses Ctrl-C
    application.run_polling()

if __name__ == '__main__':
    main()
