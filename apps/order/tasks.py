from django.utils import translation

from apps.account.models import User
from apps.notification.models import Action
from apps.notification.types import NotificationActionType
from apps.order.models import Order, OrderItem
from apps.order.types import OrderType
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
            "from_user_id": from_user,
            "from_user_name": f_user.name,
            "from_user_profile_picture": f_user.profile_picture.url
            if f_user.profile_picture
            else None,
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
def send_order_item_invite_notification(
    from_user: int, to_user: int, invite_id: int, item_id: int
):
    try:
        t_user = User.objects.get(id=to_user)
        f_user = User.objects.get(id=from_user)
        order_item = OrderItem.objects.get(id=item_id)

        translation.activate(t_user.locale)
        title = _(f"{t_user.name} has sent you an invitation")
        body = _("Tap to get started")
        data = {
            "title": title,
            "body": body,
            "from_user_name": f_user.name,
            "from_user_phone_number": f_user.phone_number,
            "from_user_profile_picture": f_user.profile_picture.url
            if f_user.profile_picture
            else "",
            "item_id": order_item.id,
            "item_name": order_item.food_item.name,
            "item_price": str(order_item.food_item.price),
            "item_calorie": order_item.food_item.calorie,
            "item_picture": order_item.food_item.picture.url,
            "item_quantity": order_item.quantity,
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
def send_order_left_push_notification(order_id: int, from_user: int):
    try:
        left_user = User.objects.get(id=from_user).name
        order = Order.objects.get(id=order_id)
        notification_users = order.order_participants.all()

        for participant_user in notification_users:
            translation.activate(participant_user.user.locale)
            title = _(f"{left_user} has left the order")
            body = _("Tap to get started")
            data = {
                "notification_id": 5,
                "notification_action": "ORDER_LEFT",
                "title": title,
                "body": body,
                "left_user_id": from_user,
                "left_user_name": left_user,
                "order_id": order_id,
            }
            print(f"{participant_user}: {data}")
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


@app.task
def send_order_item_removed_notification(
    from_user: int, order_id: int, order_item_id: int
):
    removed_by_name = User.objects.get(id=from_user).name

    order = Order.objects.get(id=order_id)
    notification_users = order.order_participants.all().exclude(user__id=from_user)

    for participant_user in notification_users:
        translation.activate(participant_user.user.locale)
        title = _(f"{removed_by_name} has removed a item")
        body = _("Tap to see")
        data = {
            "notification_id": 6,
            "notification_action": "REMOVED_ITEM",
            "title": title,
            "body": body,
            "order_item_id": order_item_id,
            "order_id": order_id,
        }
        send_push_notification(participant_user.user, title, body, data)
        translation.deactivate()


@app.task
def send_order_item_invitation_accept_notification(
    from_user: int, order_id: int, item_id: int
):
    try:
        joined_user = User.objects.get(id=from_user).name
        order = Order.objects.get(id=order_id)
        notification_users = order.order_participants.all().exclude(user__id=from_user)
        for participant_user in notification_users:
            translation.activate(participant_user.user.locale)
            title = _(f"{joined_user} has accepted to share the item.")
            body = _("Tap to get started")
            data = {
                "notification_id": 7,
                "notification_action": "FOOD_ITEM_INVITATION_ACCEPTED",
                "title": title,
                "body": body,
                "joined_user": from_user,
                "join_user_name": joined_user,
                "order_id": order_id,
            }
            print(f"{participant_user}: {data}")
            send_push_notification(participant_user.user, title, body, data)
            translation.deactivate()
    except:
        pass


@app.task
def send_new_order_items_confirmed_notification(order_id: int):
    try:
        order = Order.objects.get(id=order_id)
        translation.activate(order.restaurant.locale)
        if order.order_type is OrderType.IN_HOUSE:
            title = f"ORDER #{order.id} A new Table order just arrived from Table #{order.table_id}."
        else:
            title = f"ORDER #{order.id} A new Pickup order just arrived."

        body = _("See the dashboard for details")
        data = {
            "notification_id": 8,
            "notification_action": "NEW_ORDER",
            "title": title,
            "body": body,
            "order_id": order_id,
        }

        if order.order_type is OrderType.IN_HOUSE:
            message = f"ORDER #{order.id} A new Table order just arrived from {order.table_id}."
            message_in_ar = f"ORDER #{order.id} A new Table order just arrived from {order.table_id}."
            action_type = NotificationActionType.RESTAURANT_NEW_TABLE_ORDER
        else:
            message = f"ORDER #{order.id} A new Table order just arrived from {order.table_id}."
            message_in_ar = f"ORDER #{order.id} A new Table order just arrived from {order.table_id}."
            action_type = NotificationActionType.RESTAURANT_NEW_TABLE_ORDER

        Action.objects.create(
            message=message,
            message_in_ar=message_in_ar,
            action_type=action_type,
            user=order.restaurant,
            sender=order.created_by,
            extra_data=data,
        )

        send_push_notification(order.restaurant, _(title), body, data)
        translation.deactivate()
    except:
        pass


@app.task
def send_update_order_items_confirmed_notification(order_id: int):
    try:
        order = Order.objects.get(id=order_id)
        translation.activate(order.restaurant.locale)
        title = _(
            f"A new item just added to the order #{order_id} from {order.table_id}."
        )
        body = _("See the dashboard for details")
        data = {
            "notification_id": 9,
            "notification_action": "UPDATE_ORDER",
            "title": title,
            "body": body,
            "order_id": order_id,
        }
        send_push_notification(order.restaurant, title, body, data)
        translation.deactivate()

        message = (
            f"A new item just added to the order #{order_id} from {order.table_id}."
        )
        message_in_ar = (
            f"A new item just added to the order #{order_id} from {order.table_id}."
        )
        action_type = NotificationActionType.RESTAURANT_NEW_ITEM_IN_ORDER

        Action.objects.create(
            message=message,
            message_in_ar=message_in_ar,
            action_type=action_type,
            user=order.restaurant,
            sender=order.created_by,
            extra_data=data,
        )
    except:
        pass


@app.task
def send_update_order_items_confirmed_customer_notification(
    from_user: int, order_id: int
):
    try:
        order = Order.objects.get(id=order_id)
        notification_users = order.order_participants.all().exclude(user__id=from_user)
        for participant_user in notification_users:
            translation.activate(participant_user.user.locale)
            title = _(f"Order items has been confirmed")
            body = _("Tap to see more")
            data = {
                "notification_id": 10,
                "notification_action": "FOOD_ITEMS_CONFIRMED",
                "title": title,
                "body": body,
                "order_id": order_id,
            }
            send_push_notification(participant_user.user, title, body, data)
            translation.deactivate()
    except:
        pass


@app.task
def send_order_will_be_ready_in_x_notification(order_id: int, time: int):
    try:
        order = Order.objects.get(id=order_id)
        notification_users = order.order_participants.all()
        for participant_user in notification_users:
            translation.activate(participant_user.user.locale)
            title = _(f"{order.restaurant.name}")
            body = _(f"Your order will be ready in {time} minutes.")
            data = {
                "notification_id": 13,
                "notification_action": "ORDER_WILL_BE_READY",
                "title": title,
                "body": body,
                "order_id": order_id,
            }
            send_push_notification(participant_user.user, title, body, data)
            translation.deactivate()
    except:
        pass


@app.task
def send_order_is_ready_notification(order_id: int):
    try:
        order = Order.objects.get(id=order_id)
        notification_users = order.order_participants.all()
        for participant_user in notification_users:
            translation.activate(participant_user.user.locale)
            title = _(f"{order.restaurant.name}")
            body = _(f"Your order is ready.")
            data = {
                "notification_id": 14,
                "notification_action": "ORDER_IS_READY",
                "title": title,
                "body": body,
                "order_id": order_id,
            }
            send_push_notification(participant_user.user, title, body, data)
            translation.deactivate()
    except:
        pass


@app.task
def send_order_is_delivered_notification(order_id: int):
    try:
        order = Order.objects.get(id=order_id)
        notification_users = order.order_participants.all()
        for participant_user in notification_users:
            translation.activate(participant_user.user.locale)
            title = _(f"{order.restaurant.name}")
            body = _(f"Your order is delivered.")
            data = {
                "notification_id": 14,
                "notification_action": "ORDER_IS_READY",
                "title": title,
                "body": body,
                "order_id": order_id,
            }
            send_push_notification(participant_user.user, title, body, data)
            translation.deactivate()
            # TODO: Mark order as completed if it is a pickup order.
    except:
        pass


@app.task
def send_order_edit_notification(from_user: int, order_id: int):
    try:
        joined_user = User.objects.get(id=from_user).name
        order = Order.objects.get(id=order_id)
        notification_users = order.order_participants.all().exclude(user__id=from_user)
        for participant_user in notification_users:
            translation.activate(participant_user.user.locale)
            title = _(f"Order has been updated")
            body = _("Tap to get started")
            data = {
                "notification_id": 15,
                "notification_action": "ORDER_ITEM_EDITED",
                "title": title,
                "body": body,
                "joined_user": from_user,
                "join_user_name": joined_user,
                "order_id": order_id,
            }
            print(f"{participant_user}: {data}")
            send_push_notification(participant_user.user, title, body, data)
            translation.deactivate()
    except:
        pass


@app.task
def send_order_accepted_notification(order_id: int):
    try:
        order = Order.objects.get(id=order_id)
        notification_users = order.order_participants.all()
        for participant_user in notification_users:
            translation.activate(participant_user.user.locale)
            title = _(f"{order.restaurant.name}")
            body = _(f"Your order has been accepted.")
            data = {
                "notification_id": 19,
                "notification_action": "ORDER_ACCEPTED",
                "title": title,
                "body": body,
                "order_id": order_id,
            }
            send_push_notification(participant_user.user, title, body, data)
            translation.deactivate()
    except:
        pass


@app.task
def send_order_rejected_notification(order_id: int):
    try:
        order = Order.objects.get(id=order_id)
        notification_users = order.order_participants.all()
        for participant_user in notification_users:
            translation.activate(participant_user.user.locale)
            title = _(f"{order.restaurant.name}")
            body = _(f"Your order has been rejected.")
            data = {
                "notification_id": 18,
                "notification_action": "ORDER_REJECTED",
                "title": title,
                "body": body,
                "order_id": order_id,
            }
            send_push_notification(participant_user.user, title, body, data)
            translation.deactivate()
    except:
        pass
