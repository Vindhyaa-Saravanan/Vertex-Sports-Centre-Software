# vertex/app/public/email.py

from flask_mail import Message
import config 
from app.extensions import mail


def send_email(recipient, subject, email_template):
    """
    Sends email to recipient, having a subject and template as entered in arguments.
    """
    # Define the email message
    msg = Message(
        subject,
        recipients = [recipient],
        html = email_template,
        sender = config.MAIL_DEFAULT_SENDER)
    
    # Send the email
    mail.send(msg)