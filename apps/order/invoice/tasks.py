from django.utils import translation

from apps.order.models import Order
from conf.celery import app
from utils.fcm import send_push_notification

_ = translation.ugettext


@app.task
def send_checkout_push_notification_to_other_users(from_user: int, order_id: int):
    try:
        order = Order.objects.get(id=order_id)
        notification_users = order.order_participants.all().exclude(user__id=from_user)
        for participant_user in notification_users:
            translation.activate(participant_user.user.locale)
            title = _(f"Please checkout")
            body = _("Tap to see more")
            data = {
                "notification_id": 11,
                "notification_action": "ORDER_MARKED_AS_CHECKOUT_CUSTOMER",
                "title": title,
                "body": body,
                "order_id": order_id,
            }
            send_push_notification(participant_user.user, title, body, data)
            translation.deactivate()
    except:
        pass


@app.task
def send_checkout_push_notification_to_the_restaurant(order_id: int):
    try:
        order = Order.objects.get(id=order_id)
        translation.activate(order.restaurant.user.locale)
        title = _(f"Order {order_id} has been marked for checkout")
        body = _("Tap to see more")
        data = {
            "notification_id": 12,
            "notification_action": "ORDER_MARKED_AS_CHECKOUT_RESTAURANT",
            "title": title,
            "body": body,
            "order_id": order_id,
        }
        send_push_notification(order.restaurant.user, title, body, data)
        translation.deactivate()

    except:
        pass
