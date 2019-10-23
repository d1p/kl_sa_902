import requests
from django.conf import settings


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
