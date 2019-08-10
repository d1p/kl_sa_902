from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import Customer
from .tasks import generate_qr_code
from io import BytesIO

import qrcode


@receiver(post_save, sender=Customer)
def post_customer_account_registration(sender, instance, created, *args, **kwargs):
    if created is True:
        generate_qr_code.delay(instance.id)
