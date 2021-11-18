import os
import smtplib
from email import encoders
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
from email.mime.multipart import MIMEMultipart
from os.path import join, dirname
from dotenv import load_dotenv


class Mailer:
    def __init__(self, receivers, subject, body):
        dotenv_path = join(dirname(__file__), '.env')
        load_dotenv(dotenv_path)
        self.sender = f"{os.getenv('SENDER_NAME')} <{os.getenv('SENDER_EMAIL')}>" if os.getenv('SENDER_EMAIL') else None
        self.receivers = receivers
        self.subject = subject
        self.body = body
        self.server = os.getenv('SMTP_SERVER') if os.getenv('SMTP_SERVER') else None

    def send(self):
        msg = MIMEMultipart()
        msg['From'] = self.sender
        msg['To'] = self.receivers
        msg['Subject'] = self.subject
        msg.attach(MIMEText(self.body, 'plain'))
        server = smtplib.SMTP(self.server)
        text = msg.as_string()
        server.sendmail(self.sender, self.receivers, text)
        server.quit()

    def send_with_attachment(self, attachment):
        msg = MIMEMultipart()
        msg['From'] = self.sender
        msg['To'] = self.receivers
        msg['Subject'] = self.subject
        msg.attach(MIMEText(self.body, 'plain'))
        part = MIMEBase('application', 'octet-stream')
        part.set_payload(open(attachment, 'rb').read())
        encoders.encode_base64(part)
        part.add_header('Content-Disposition', 'attachment; filename="%s"' % os.path.basename(attachment))
        msg.attach(part)
        server = smtplib.SMTP(self.server)
        text = msg.as_string()
        server.sendmail(self.sender, self.receivers, text)
        server.quit()


def prompt(prompt):
    return input(prompt).strip()


def sendmail(recipient='', subject='', body=''):
    if not recipient or not subject or not body:
        print("Please enter the following information...\n")
    recipient = recipient if recipient else prompt("Recipient: ")
    subject = subject if subject else prompt("Subject: ")
    body = body if body else prompt("Body: ")
    print("Sending...")
    mailer = Mailer(recipient, subject, body)
    mailer.send()
    print("Sent!")


def sendmail_with_attachment(recipient='', subject='', body='', attachment=''):
    if not recipient or not subject or not body or not attachment:
        print("Please enter the following information...\n")
    recipient = recipient if recipient else prompt("Recipient: ")
    subject = subject if subject else prompt("Subject: ")
    body = body if body else prompt("Body: ")
    attachment = attachment if attachment else prompt("Attachment: ")
    print("Sending...")
    mailer = Mailer(recipient, subject, body)
    mailer.send_with_attachment(attachment)
    print("Sent!")