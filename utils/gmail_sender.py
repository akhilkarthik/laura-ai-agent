import os
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart


def send_email(to: str, subject: str, body: str):
    gmail_address = os.getenv("GMAIL_ADDRESS")
    app_password = os.getenv("GMAIL_APP_PASSWORD")

    if not gmail_address or not app_password:
        raise ValueError("GMAIL_ADDRESS and GMAIL_APP_PASSWORD not set")

    msg = MIMEMultipart()
    msg["From"] = gmail_address
    msg["To"] = to
    msg["Subject"] = subject
    msg.attach(MIMEText(body, "plain"))

    with smtplib.SMTP_SSL("smtp.gmail.com", 465) as server:
        server.login(gmail_address, app_password.replace(" ", ""))
        server.send_message(msg)
