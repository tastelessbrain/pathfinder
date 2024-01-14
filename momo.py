import logging
import json
import os
import subprocess
from telegram import Update
from telegram.ext import Application, MessageHandler, CallbackQueryHandler, filters, ContextTypes

# Enable logging
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    level=logging.CRITICAL)

logger = logging.getLogger(__name__)

# Define a function to handle incoming messages
async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    message = update.message
    # Log the received message
    logger.info(f'Received message: {message.text}')
    # Print the received message to the console
    print(f'Received message: {message.text}')

# Define a function to handle callback queries (button presses)
async def handle_callback_query(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    query = update.callback_query
    await query.answer()  # This is necessary to acknowledge the callback query

    # Extract and log the callback data
    callback_data = query.data
    logger.info(f'Received callback data: {callback_data}')
    print(f'Received callback data: {callback_data}')

    subprocess.run(["/usr/bin/python3", os.path.expanduser("~/pathfinder/columba.py"), callback_data])

    ## Load the saved search results
    #with open('saved_search_results.json') as f:
    #    search_results = json.load(f)
    #
    ## Get the object corresponding to the ID from the callback data
    #object_id = int(callback_data)  # Assuming the callback data is a string representation of the ID
    #
    ## Iterate over the search results to find the object with the given ID
    #for result in search_results:
    #    if result['id'] == object_id:
    #        print(f'Object with ID {object_id}: {result}')
    #        break
    #else:
    #    print(f'No object found with ID {object_id}')

def main() -> None:
    # Create the Application and pass it your bot's token.
    application = Application.builder().token('6597287234:AAEDgR2GkUUfoaBGg-eI0tWbVqtO8lr_qFQ').build()

    # Register the message handler
    application.add_handler(MessageHandler(filters.TEXT, handle_message))

    # Register the callback query handler
    application.add_handler(CallbackQueryHandler(handle_callback_query))

    # Run the bot until the user presses Ctrl-C
    application.run_polling()

if __name__ == '__main__':
    main()
