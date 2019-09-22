from django.utils import translation

from apps.account.models import User
from conf.celery import app
from utils.fcm import send_push_notification

_ = translation.ugettext_lazy


@app.task
def send_order_invite_notification(from_user: User, to_user: User, invite_id: int):
    translation.activate(to_user.locale)
    title = _(f"{from_user.name} has sent you an invitation")
    body = _("Tap to get started")
    data = {
        "title": title,
        "body": body,
        "from_user": from_user.id,
        "to_user": to_user.id,
        "invite_id": invite_id,
    }
    send_push_notification(to_user, title, body, data)
    translation.deactivate()
