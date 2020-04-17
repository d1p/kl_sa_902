from decimal import Decimal

import requests
from django.conf import settings

from apps.account.restaurant.models import Restaurant
from apps.order.invoice.models import InvoiceItem
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
    response = requests.post("https://www.paytabs.com/apiv3/release_capture_preauth", data=data)
    response_data = response.json()
    return response_data


def process_new_completed_order_earning(order: Order):
    restaurant: Restaurant = order.restaurant.restaurant

    try:
        total = Decimal(0.0)
        for invoice_item in order.invoice.invoice_items.all():
            total += invoice_item.amount

        earning = (total / Decimal(100)) * order.invoice.order_cut
        if order.order_type is OrderType.PICK_UP:
            restaurant.pickup_earning += earning
        elif order.order_type is OrderType.IN_HOUSE:
            restaurant.inhouse_earning += earning

        restaurant.total_earning += earning
        restaurant.save()
    except:
        print(f"Something went wrong in process_new_completed_order_earning({order.id}")
