from django.contrib.auth.models import User
from django.utils import translation

from apps.order.invoice.models import Invoice, Transaction
from apps.order.invoice.types import PaymentStatus
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

@app.task
def send_single_bill_paid_notification(invoice_id: int, user_id: int, transaction_id: int):
    try:
        user = User.objects.get(id=user_id)
        transaction = Transaction.objects.get(id=transaction_id)

        invoice = Invoice.objects.get(id=invoice_id)
        paid_transaction = Transaction.objects.filter(
            order=invoice.order,
            transaction_status__in=[PaymentStatus.AUTHORIZED, PaymentStatus.SUCCESSFUL],
        )
        paid_transaction_users = [user for user in paid_transaction]

        for participant_user in invoice.order.order_participants.all():
            if participant_user not in paid_transaction_users:
                translation.activate(participant_user.user.locale)
                title = _(f"{user.get_full_name()} has paid bill.")
                body = _("Tap to see more")
                data = {
                    "notification_id": 17,
                    "notification_action": "ORDER_SINGLE_USER_PAID",
                    "title": title,
                    "body": body,
                    "order_id": invoice.order_id,
                    "invoice_id": invoice.id,
                    "paid_for": [invoice_item.user_id for invoice_item in transaction.invoice_items.all()],
                }
                send_push_notification(participant_user.user, title, body, data)
                translation.deactivate()

        translation.activate(invoice.order.restaurant.locale)
        title = _(f"{user.get_full_name()} has paid bill.")
        body = _("Tap to see more")
        data = {
            "notification_id": 17,
            "notification_action": "ORDER_SINGLE_USER_PAID",
            "title": title,
            "body": body,
            "order_id": invoice.order_id,
            "invoice_id": invoice.id,
            "paid_for": [invoice_item.user_id for invoice_item in transaction.invoice_items.all()],
        }
        send_push_notification(invoice.order.restaurant, title, body, data)
        translation.deactivate()

    except:
        pass

@app.task
def send_all_bill_paid_notification(order_id: int):
    try:
        order = Order.objects.get(id=order_id)
        paid_transaction = Transaction.objects.filter(
            order=order,
            transaction_status__in=[PaymentStatus.AUTHORIZED, PaymentStatus.SUCCESSFUL],
        )
        paid_transaction_users = [user for user in paid_transaction]
        for participant_user in order.order_participants.all():
            if participant_user not in paid_transaction_users:
                translation.activate(participant_user.user.locale)
                title = _(f"Bill has been paid")
                body = _("Tap to get started")
                data = {
                    "notification_id": 16,
                    "notification_action": "ORDER_ALL_BILL_PAID",
                    "title": title,
                    "body": body,
                    "order_id": order_id,
                }
                print(f"{participant_user}: {data}")
                send_push_notification(participant_user.user, title, body, data)
                translation.deactivate()

    except:
        pass
