from decimal import Decimal

import requests
from django.conf import settings
from django.db import transaction

from apps.account.restaurant.models import Restaurant
from apps.order.invoice.models import Invoice
from apps.order.models import Order
from apps.order.types import OrderType


def verify_transaction(transaction_id):
    data = {
        "merchant_email": settings.PAYTABS_MERCHANT_EMAIL,
        "secret_key": settings.PAYTABS_SECRET_KEY,
        "transaction_id": transaction_id,
    }

    response = requests.post(settings.PAYTABS_VERIFY_PAYMENT_URL, data=data)
    response_data = response.json()
    return response_data


def capture_transaction(transaction_id, amount):
    data = {
        "merchant_email": settings.PAYTABS_MERCHANT_EMAIL,
        "secret_key": settings.PAYTABS_SECRET_KEY,
        "transaction_id": transaction_id,
        "amount": amount,
    }
    response = requests.post(
        "https://www.paytabs.com/apiv3/release_capture_preauth", data=data
    )
    response_data = response.json()
    return response_data


def process_new_completed_order_earning(order: Order):
    with transaction.atomic():

        restaurant: Restaurant = order.restaurant.restaurant
        total = Decimal(0.0)
        try:
            invoice = Invoice.objects.get(order=order)
        except Invoice.DoesNotExist:
            raise ValueError("Invoice does not exists")

        if invoice.app_earning is not None and invoice.restaurant_earning is not None:
            return False

        for invoice_item in invoice.invoice_items.all():
            total += invoice_item.amount

        app_earning = (total / Decimal(100)) * invoice.order_cut
        restaurant_earning = total - app_earning

        app_earning = Decimal(round(app_earning, 3))
        restaurant_earning = Decimal(round(restaurant_earning, 3))

        if order.order_type is OrderType.PICK_UP:
            restaurant.app_pickup_earning += app_earning
            restaurant.pickup_earning += restaurant_earning
        elif order.order_type is OrderType.IN_HOUSE:
            restaurant.app_inhouse_earning += app_earning
            restaurant.inhouse_earning += restaurant_earning

        restaurant.total_earning += restaurant_earning
        restaurant.app_total_earning += app_earning

        restaurant.total += total

        restaurant.save()

        invoice.app_earning = app_earning
        invoice.restaurant_earning = restaurant_earning
        invoice.save()
