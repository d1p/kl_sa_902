from django.db import models

from apps.account.models import User
from apps.order.models import Order


class Customer(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    qr_code = models.ImageField()


class Misc(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    last_order = models.ForeignKey(
        Order, on_delete=models.SET_NULL, null=True, blank=True
    )
