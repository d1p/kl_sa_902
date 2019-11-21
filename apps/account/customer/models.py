from django.db import models

from apps.account.models import User
from apps.account.restaurant.models import Restaurant
from apps.order.models import Order
from .types import CustomerMiscType


class Customer(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    qr_code = models.ImageField()


class Misc(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    last_order = models.ForeignKey(
        Order, on_delete=models.SET_NULL, null=True, blank=True
    )

    last_order_in_checkout = models.BooleanField(default=False, db_index=True)
    last_order_in_rating = models.BooleanField(default=False, db_index=True)

    state = models.CharField(
        max_length=40,
        db_index=True,
        choices=CustomerMiscType.choices,
        default=CustomerMiscType.IN_ORDER,
    )

    updated_at = models.DateTimeField(auto_now=True)

    def last_restaurant(self) -> int:
        return self.last_order.restaurant.id if self.last_order else None

    def last_order_type(self) -> int:
        return self.last_order.order_type if self.last_order else None

    def set_new_order(self, order: Order):
        self.last_order = order
        self.last_order_in_checkout = False
        self.last_order_in_rating = False
        self.state = CustomerMiscType.IN_ORDER
        self.save()

    def set_no_order(self):
        self.last_order = None
        self.last_order_in_checkout = False
        self.last_order_in_rating = False
        self.state = CustomerMiscType.NO_ORDER
        self.save()

    def set_order_in_checkout(self):
        self.last_order_in_checkout = True
        self.state = CustomerMiscType.IN_CHECKOUT
        self.save()

    def set_order_in_rating(self):
        self.last_order_in_checkout = False
        self.last_order_in_rating = True
        self.state = CustomerMiscType.IN_RATING
        self.save()
