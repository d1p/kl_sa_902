from conf.celery import app
from apps.account.models import User
from django.utils import translation
from utils.fcm import send_push_notification


@app.task
def send_order_invite_notification(from_user: User, to_user: User, order_id: int):
    translation.activate(to_user.locale)
    title = _("")
    body = _("")
    data = {
        "title": title,
        "body": body,
        "from_user": from_user.id,
        "to_user": to_user.id,
        "order_id": order_id,
    }
    send_push_notification(to_user, title, body, data)
    translation.deactivate()
