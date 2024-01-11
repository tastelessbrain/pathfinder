import os
import sys
import json
import telegram #import telegram bot library for telegram message handling
import asyncio #on my scale not really necessary but needed for telegram message handling to work
from dotenv import load_dotenv #import .env file
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
import logging

#load .env file
load_dotenv()

####################
###Mail_templates###
female_mail_template = """
Sehr geehrte Frau {name_contact},

ich interessiere mich sehr für die inserierte {room_count}-Zimmer-Wohnung unter der Adresse: {adress}.

Mein Name ist Mario Breunig, ich bin 26 Jahre alt und derzeit als Fachinformatiker bei der Continum Ag tätig.
Die Möglichkeit, in einer Wohnung wie dieser zu leben, weckt großes Interesse bei mir.

Aktuell suche ich dringend nach einer neuen Wohnmöglichkeit, die meinen Bedürfnissen besser entspricht als meine derzeitige Lage, da ich für sehr wenig Wohnfläche zu viel Geld bezahlen muss.
Zudem steht seitens der Vermieter eine Anmeldung von Eigenbedarf im Raum.

Finanziell bin ich in der Lage, die anfallenden Kosten der Wohnung zu tragen, und freue mich auf die Chance, Teil der Baugenossenschaft zu werden, und auf diese Art nicht nur Wohnraum, sondern auch ein positives und engagiertes Miteinander zu fördern.

Für Rückfragen stehe ich Ihnen gerne zur Verfügung.
Sie erreichen mich per:
E-Mail: {my_email},
Telfefon: {my_phone}

Vielen Dank für Ihre Zeit und die Berücksichtigung meiner Bewerbung.

Mit freundlichen Grüßen,
Mario Breunig"""

male_mail_template = """
Sehr geehrter Herr {name_contact},

ich interessiere mich sehr für die inserierte {room_count}-Zimmer-Wohnung unter der Adresse: {adress}.

Mein Name ist Mario Breunig, ich bin 26 Jahre alt und derzeit als Fachinformatiker bei der Continum Ag tätig.
Die Möglichkeit, in einer Wohnung wie dieser zu leben, weckt großes Interesse bei mir.

Aktuell suche ich dringend nach einer neuen Wohnmöglichkeit, die meinen Bedürfnissen besser entspricht als meine derzeitige Lage, da ich für sehr wenig Wohnfläche zu viel Geld bezahlen muss.
Zudem steht seitens der Vermieter eine Anmeldung von Eigenbedarf im Raum.

Finanziell bin ich in der Lage, die anfallenden Kosten der Wohnung zu tragen, und freue mich auf die Chance, Teil der Baugenossenschaft zu werden, und auf diese Art nicht nur Wohnraum, sondern auch ein positives und engagiertes Miteinander zu fördern.

Für Rückfragen stehe ich Ihnen gerne zur Verfügung.
Sie erreichen mich per:
E-Mail: {my_email},
Telfefon: {my_phone}

Vielen Dank für Ihre Zeit und die Berücksichtigung meiner Bewerbung.

Mit freundlichen Grüßen,
Mario Breunig"""
####################

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
    # Configure logging
    logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')
    
    # Your Outlook account credentials
    outlook_user = os.getenv("OUTLOOK_USER")
    outlook_password = os.getenv("OUTLOOK_PASSSWORD")

    #personal data
    self_phone_number = os.getenv("MY_PHONE_NUMBER")
    print(self_phone_number)

    #maildata
    mail_to = flat_data['Mail']
    mail_bcc = "acc.register@outlook.de"
    mail_subject = f"Bewerbung auf die {flat_data['Zimmer']}-Zimmer Wohnung | {flat_data['Adresse']}."

    # Create the email
    msg = MIMEMultipart()
    msg['From'] = outlook_user
    msg['To'] = mail_to  # Replace with the recipient's email address
    msg['Bcc'] = mail_bcc  # Replace with the BCC email address
    msg['Subject'] = mail_subject

    
    if flat_data["Kontakt"] == "Johannes Kronfeld":
        body = male_mail_template.format(
            name_contact = flat_data['Kontakt'].split()[-1],
            room_count=flat_data['Zimmer'],
            adress=flat_data['Adresse'],
            my_email=outlook_user,
            my_phone=self_phone_number
        )
    else:
        # The body of the email
        body = female_mail_template.format(
            name_contact = flat_data['Kontakt'].split()[-1],
            room_count=flat_data['Zimmer'],
            adress=flat_data['Adresse'],
            my_email=outlook_user,
            my_phone=self_phone_number
        )
    msg.attach(MIMEText(body, 'plain'))

    # Send the email
    try:
        server = smtplib.SMTP('smtp-mail.outlook.com', 587)
        server.starttls()
        server.login(outlook_user, outlook_password)
        text = msg.as_string()
        server.sendmail(outlook_user, [mail_to, mail_bcc], text)  # Replace with the recipient's email address and BCC email address
        server.quit()
        logging.info("Email sent successfully")
    except Exception as e:
        logging.error("Failed to send email: %s", str(e))

def main():
    saved_flats = load_flats()
    object_id = get_passed_data()
    data = load_data_with_id(saved_flats, object_id)
    print(data)
    send_email(data)


if __name__ == '__main__':
    main()