from django.utils import translation

from apps.account.models import User
from apps.order.models import Order, OrderItem
from conf.celery import app
from utils.fcm import send_push_notification

_ = translation.ugettext


@app.task
def send_order_invite_notification(from_user: int, to_user: int, invite_id: int):
    try:
        t_user = User.objects.get(id=to_user)
        f_user = User.objects.get(id=from_user)

        translation.activate(t_user.locale)

        title = _(f"{f_user.name} has sent you an invitation")
        body = _("Tap to get started")
        data = {
            "title": title,
            "body": body,
            "from_user": {
                "id": from_user,
                "name": f_user.name,
                "profile_picture": f_user.profile_picture.url,
            },
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
def send_order_item_invite_notification(from_user: int, to_user: int, invite_id: int, item_id: int):
    try:
        t_user = User.objects.get(id=to_user)
        f_user = User.objects.get(id=from_user)
        order_item = OrderItem.objects.get(id=item_id).select_related("food_item")

        translation.activate(t_user.locale)
        title = _(f"{t_user.name} has sent you an invitation")
        body = _("Tap to get started")
        data = {
            "title": title,
            "body": body,
            "from_user": {
                "name": f_user.name,
                "phone_number": f_user.phone_number,
                "profile_picture": f_user.profile_picture.url,
            },
            "item": {
                "id": order_item.id,
                "name": order_item.food_item.name,
                "price": order_item.food_item.price,
                "calorie": order_item.food_item.calorie,
                "picture": order_item.food_item.picture.url,
                "quantity": order_item.quantity,
            },
            "to_user": to_user,
            "invite_id": invite_id,
            "notification_id": 4,
            "notification_action": "NEW_FOOD_ITEM_INVITATION",
        }
        send_push_notification(t_user, title, body, data)
        translation.deactivate()

    except User.DoesNotExist:
        pass


@app.task
def send_order_invitation_accept_notification(from_user: int, order_id: int):
    try:
        joined_user = User.objects.get(id=from_user).name
        order = Order.objects.get(id=order_id)
        notification_users = order.order_participants.all().exclude(user__id=from_user)
        for participant_user in notification_users:
            translation.activate(participant_user.user.locale)
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
            send_push_notification(participant_user.user, title, body, data)
            translation.deactivate()
    except:
        pass


@app.task
def send_new_order_in_cart_notification(
    added_by: int, order_id: int, order_item_id: int
):
    added_by_name = User.objects.get(id=added_by).name

    order = Order.objects.get(id=order_id)
    notification_users = order.order_participants.all().exclude(user__id=added_by)

    for participant_user in notification_users:
        translation.activate(participant_user.user.locale)
        title = _(f"{added_by_name} has added a new item")
        body = _("Tap to see")
        data = {
            "notification_id": 3,
            "notification_action": "NEW_ITEM",
            "title": title,
            "body": body,
            "order_item_id": order_item_id,
            "added_by_name": added_by_name,
            "order_id": order_id,
        }
        send_push_notification(participant_user.user, title, body, data)
        translation.deactivate()
