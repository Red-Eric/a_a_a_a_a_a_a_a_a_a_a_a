from email.message import EmailMessage
from aiosmtplib import send
from app.config import config

async def send_email(subject: str, to: str, body: str):
    message = EmailMessage()
    message["From"] = config.FROM_EMAIL
    message["To"] = to
    message["Subject"] = subject

    message.set_content("Ce message contient du HTML. Veuillez utiliser un client compatible.")

    message.add_alternative(body, subtype="html")

    await send(
        message,
        hostname=config.SMTP_HOST,
        port=config.SMTP_PORT,
        start_tls=True,
        username=config.SMTP_USER,
        password=config.SMTP_PASS,
    )
