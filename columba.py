import os
import sys
import json
import telegram #import telegram bot library for telegram message handling
import asyncio #on my scale not really necessary but needed for telegram message handling to work
from dotenv import load_dotenv #import .env file
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

#load .env file
load_dotenv()

#send a telegram message through the bot | api token and chat id are stored in .env file
async def send_telegram_message(message):
    bot_token = os.getenv("TELEGRAM_BOT_TOKEN")
    chat_id = os.getenv("TELEGRAM_CHAT_ID")
    bot = telegram.Bot(bot_token)
    async with bot:
        await bot.send_message(text=message, chat_id=chat_id)

def load_flats():
    with open('saved_search_results.json') as f:
        saved_flats = json.load(f)
        #print(saved_flats)
        return saved_flats

def get_passed_data():
    # Check if an argument was passed
    print(len(sys.argv))
    if len(sys.argv) == 2:
        arg = int(sys.argv[1])
        print(arg)
        return arg
        
    else:
        asyncio.run(send_telegram_message(f"An Error occured while passing Reply-Data to Columba.\nMaybe wrong number of args.\nPassed-Data: {sys.argv}"))

def load_data_with_id(saved_flats, object_id):
    flat = saved_flats[object_id - 1]
    return flat

def send_email(flat_data):
    # Your Outlook account credentials
    outlook_user = os.getenv("OUTLOOK_USER")
    outlook_password = os.getenv("OUTLOOK_PASSWORD")

    # Create the email
    msg = MIMEMultipart()
    msg['From'] = outlook_user
    msg['To'] = 'acc.register@outlook.de'  # Replace with the recipient's email address
    msg['Subject'] = 'New flat found'

    # The body of the email
    body = f"""
    New flat found:

    Link: {flat_data['Link']}
    Kontakt: {flat_data['Kontakt']}
    Mail: {flat_data['Mail']}
    Telefon: {flat_data['Telefon']}
    """
    msg.attach(MIMEText(body, 'plain'))

    # Send the email
    server = smtplib.SMTP('smtp-mail.outlook.com', 587)
    server.starttls()
    server.login(outlook_user, outlook_password)
    text = msg.as_string()
    server.sendmail(outlook_user, 'acc.register@outlook.de', text)  # Replace with the recipient's email address
    server.quit()

def main():
    saved_flats = load_flats()
    object_id = get_passed_data()
    data = load_data_with_id(saved_flats, object_id)
    print(data)
    send_email(data)


if __name__ == '__main__':
    main()