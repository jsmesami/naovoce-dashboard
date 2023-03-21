import smtplib
import ssl
from email.message import EmailMessage


def send_email(app, *, sender="software@na-ovoce.cz", recipient, subject, body):
    user = app.config.get("EMAIL_USER")
    password = app.config.get("EMAIL_PASSWORD")
    host = app.config.get("EMAIL_HOST")
    port = app.config.get("EMAIL_PORT")
    secure = not app.config.get("DEBUG", True)

    msg = EmailMessage()
    msg.set_content(body)
    msg["Subject"] = subject
    msg["From"] = sender
    msg["To"] = recipient

    with smtplib.SMTP(host, port) as server:
        if secure:
            server.starttls(context=ssl.create_default_context())
            server.login(user=user, password=password)

        server.send_message(msg)
