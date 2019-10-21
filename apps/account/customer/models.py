from django.db import models

from apps.account.models import User
from apps.account.restaurant.models import Restaurant
from apps.order.models import Order


class Customer(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    qr_code = models.ImageField()


class Misc(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    last_order = models.ForeignKey(
        Order, on_delete=models.SET_NULL, null=True, blank=True
    )
    last_order_in_checkout = models.BooleanField(default=False, db_index=True)
    last_restaurant = models.ForeignKey(User, on_delete=models.CASCADE, null=True, related_name="last_restaurant_user")
    last_order_type = models.IntegerField(null=True)
