from django.utils import translation

from apps.account.models import User
from conf.celery import app
from utils.fcm import send_push_notification

_ = translation.ugettext_lazy


@app.task
def send_order_invite_notification(from_user: int, to_user: int, invite_id: int):
    try:
        t_user = User.objects.get(id=to_user)
        translation.activate(t_user.locale)
        title = _(f"{t_user.name} has sent you an invitation")
        body = _("Tap to get started")
        data = {
            "title": title,
            "body": body,
            "from_user": from_user,
            "to_user": to_user,
            "invite_id": invite_id,
        }
        send_push_notification(t_user, title, body, data)
        translation.deactivate()

    except User.DoesNotExist:
        pass
