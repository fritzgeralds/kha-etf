import os
from dotenv import load_dotenv

class Config(object):
    def __init__(self):
        load_dotenv()
        self.environment = os.getenv("ENVIRONMENT")
        self.sender_name = os.getenv("SENDER_NAME")
        self.sender_email = os.getenv("SENDER_EMAIL")
        self.smtp_server = os.getenv("SMTP_SERVER")
        self.smtp_port = os.getenv("SMTP_PORT") or 25
        self.smtp_user = os.getenv("SMTP_USER")
        self.smtp_password = os.getenv("SMTP_PASSWORD")
        self.smtp_tls = os.getenv("SMTP_TLS") or False
        self.smtp_ssl = os.getenv("SMTP_SSL") or False
