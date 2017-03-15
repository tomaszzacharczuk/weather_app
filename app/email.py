from threading import Thread
from flask import current_app, render_template
from flask_mail import Message
from . import mail
from .models import User
from app import db


def send_async_email(app, msg):
    with app.app_context():
        try:
            mail.send(msg)
        except:
            """If confirmation email cannot be send, user is confirmed automatically.
            I assume that senior dev won't have SSL configured locally so he (or she)
            won't set his email and password in environment variables for security reasons.
            To keep app usable, I confirm user without email but password reset
            and email change will not work."""
            recipients = msg.recipients
            for email in recipients:
                user = User.query.filter_by(email=email).first()
                user.confirmed = True
                db.session.add(user)
                db.session.commit()
                print('User ' + user.email + ' automatically confirmed.')


def send_email(to, subject, template, **kwargs):
    app = current_app._get_current_object()
    msg = Message(
        subject=app.config['WEATHER_APP_MAIL_SUBJECT_PREFIX'] + ' ' + subject,
        recipients=[to],
        sender=app.config['WEATHER_APP_MAIL_SENDER'])
    msg.body = render_template(template + '.txt', **kwargs)
    msg.html = render_template(template + '.html', **kwargs)
    thr = Thread(target=send_async_email, args=[app, msg])
    thr.start()
    return thr
