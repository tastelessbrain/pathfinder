import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
import logging
import os
from dotenv import load_dotenv

load_dotenv()

def send_email():
    # Configure logging
    logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')

    # Your Outlook account credentials
    outlook_user = os.getenv("OUTLOOK_USER")
    outlook_password = os.getenv("OUTLOOK_PASSSWORD")
    mail_to = "mario.breunig13@gmail.com"
    mail_bcc = "acc.register@outlook.de"
    #mail_subject = f"Bewerbung auf die {Zimmer}-Zimmer Wohnung in der {Adresse}."

    # Create the email
    msg = MIMEMultipart()
    msg['From'] = outlook_user
    msg['To'] = mail_to  # Replace with the recipient's email address
    msg['Bcc'] = mail_bcc  # Replace with the BCC email address
    msg['Subject'] = 'New flat found'

    # The body of the email
    body = """
    New flat found:

    Link: https://example.com
    Kontakt: John Doe
    Mail: john.doe@example.com
    Telefon: 1234567890
    """
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

send_email()