from django.utils import translation

from apps.account.models import User
from apps.order.models import Order
from conf.celery import app

_ = translation.ugettext


@app.task
def send_checkout_push_notification_to_other_users(from_user: int, order_id: int):
    pass


@app.task
def send_checkout_push_notification_to_the_restaurant(from_user: int, order_id: int):
    pass
