from django.utils.translation import ugettext_lazy
from conf.celery import app
from apps.account.customer.models import Customer
import qrcode


@app.task
def generate_qr_code(customer: Customer):
    qr = qrcode.QRCode(
        version=2,
        error_correction=qrcode.constants.ERROR_CORRECT_L,
        box_size=10,
        border=4,
    )
    customer.qr_code = qr
    customer.save()
