from django.db.models.signals import post_save
from django.dispatch import Signal, receiver
from .models import Customer
from .tasks import generate_qr_code


@receiver(post_save, sender=Customer)
def post_customer_accout_registration(sender, instance, created, *args, **kwargs):
    if created is True:
        generate_qr_code(instance)
