from io import BytesIO

import qrcode
from django.db.models.signals import post_save
from django.dispatch import receiver

from .models import Customer


@receiver(post_save, sender=Customer)
def post_customer_account_registration(sender, instance, created, *args, **kwargs):
    if created is True:
        qr = qrcode.QRCode(
            version=2,
            error_correction=qrcode.constants.ERROR_CORRECT_L,
            box_size=10,
            border=4,
        )
        qr.add_data(instance.user.id)
        qr.make(fit=True)

        img = qr.make_image(fill_color="black", back_color="white")

        thumb_io = BytesIO()
        img.save(thumb_io, img.format, quality=100)

        instance.qr_code.save(
            f"user/customer/qr/{instance.user.id}.png", thumb_io, save=False
        )
        instance.save()
