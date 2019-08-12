from conf.celery import app
from apps.account.models import User
from django.core.mail import send_mail


@app.task
def send_new_ticket_notification():
    pass
