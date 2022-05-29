from flask_mail import Message
from appPackage import mail
from flask import current_app
from threading import Thread


def send_async_email(appF, msg):
    with appF.app_context():
        mail.send(msg)

def send_email(subject, sender, recipients, text_body, html_body):
    msg = Message(subject, sender=sender, recipients=recipients)
    msg.body = text_body
    msg.html = html_body
    Thread(target=send_async_email,
           args=(current_app._get_current_object(), msg)).start()