from django.utils import translation

from apps.account.models import User
from apps.order.models import Order
from conf.celery import app
from utils.fcm import send_push_notification

_ = translation.ugettext


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
            "notification_id": 1,
            "notification_action": "NEW_INVITATION",
        }
        send_push_notification(t_user, title, body, data)
        translation.deactivate()

    except User.DoesNotExist:
        pass


@app.task
def send_order_invitation_accept_notification(from_user: int, order_id: int):
    try:
        joined_user = User.objects.get(id=from_user).name
        Order.objects.get(id=order_id)
        notification_users = Order.order_participants.all().exclude(user__id=from_user)
        for user in notification_users:
            translation.activate(user.locale)
            title = _(f"{joined_user} has joined the order")
            body = _("Tap to get started")
            data = {
                "notification_id": 2,
                "notification_action": "INVITATION_ACCEPTED",
                "title": title,
                "body": body,
                "joined_user": from_user,
                "join_user_name": joined_user,
                "order_id": order_id,
            }
            send_push_notification(user, title, body, data)
            translation.deactivate()
    except:
        pass


@app.task
def send_new_order_in_cart_notification():
    pass
