import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

def send_email():
    # Your Outlook account credentials
    outlook_user = "Mario-Breunig@outlook.de"
    outlook_password = "wbqwbbucpnwgogay"

    # Create the email
    msg = MIMEMultipart()
    msg['From'] = outlook_user
    msg['To'] = 'acc.register@outlook.de'  # Replace with the recipient's email address
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
    server = smtplib.SMTP('smtp-mail.outlook.com', 587)
    server.starttls()
    server.login(outlook_user, outlook_password)
    text = msg.as_string()
    server.sendmail(outlook_user, 'acc.register@outlook.de', text)  # Replace with the recipient's email address
    server.quit()

send_email()