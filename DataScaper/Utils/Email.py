import smtplib
import ssl
from email.message import EmailMessage


def send_mail(subject, message):
    #    print(message)
    #    return
    email_sender = 'uchihabt03@gmail.com'
    email_password = "redacted"
    email_receiver = 'lichtut@gmail.com'

    em = EmailMessage()
    em['From'] = email_sender
    em['To'] = email_receiver
    em['Subject'] = subject
    em.set_content(message)
    with smtplib.SMTP_SSL("smtp.gmail.com", 465, context=ssl.create_default_context()) as server:
        server.login(email_sender, email_password)
        server.sendmail(email_sender, email_receiver, em.as_string())
