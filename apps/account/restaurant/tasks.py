from io import BytesIO

import qrcode

from conf.celery import app
from .models import RestaurantTable


@app.task
def generate_table_qr_code(table_id: int):
    table = RestaurantTable.objects.get(id=table_id)

    qr = qrcode.QRCode(
        version=2,
        error_correction=qrcode.constants.ERROR_CORRECT_L,
        box_size=10,
        border=4,
    )
    data = {"restaurant_id": table.user.id, "table_id": table.id}
    qr.add_data(data)
    qr.make(fit=True)

    img = qr.make_image(fill_color="black", back_color="white")
    thumb_io = BytesIO()
    img.save(thumb_io, img.format, quality=100)

    table.qr_code.save(f"user/restaurant/table/qr/{table.id}.png", thumb_io, save=False)
    table.save()
