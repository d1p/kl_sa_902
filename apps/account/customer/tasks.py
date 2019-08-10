from io import BytesIO

import qrcode

from apps.account.customer.models import Customer
from conf.celery import app


@app.task
def generate_qr_code(c: int):
    customer = Customer.objects.get(id=c)

    qr = qrcode.QRCode(
        version=2,
        error_correction=qrcode.constants.ERROR_CORRECT_L,
        box_size=10,
        border=4,
    )
    qr.add_data(customer.user.id)
    qr.make(fit=True)

    img = qr.make_image(fill_color="black", back_color="white")

    thumb_io = BytesIO()
    img.save(thumb_io, img.format, quality=100)

    customer.qr_code.save(
        f"user/customer/qr/{customer.user.id}.png", thumb_io, save=False
    )
