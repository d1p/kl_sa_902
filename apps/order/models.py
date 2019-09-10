from decimal import Decimal
from django.conf import settings
from django.db import models
from django.db.models import Q
from django.utils.translation import ugettext_lazy as _

from apps.account.models import User
from apps.account.restaurant.models import RestaurantTable
from apps.food.models import FoodItem, FoodAddOn, FoodAttributeMatrix


class Order(models.Model):
    ORDER_TYPE_CHOICES = ((0, _("Pick Up")), (1, _("In House")))
    order_type = models.SmallIntegerField(
        choices=ORDER_TYPE_CHOICES,
        help_text=_("Indicates weather the order is a Pick up order or In House "),
    )
    restaurant = models.ForeignKey(
        User, on_delete=models.SET_NULL, db_index=True, null=True
    )
    table = models.ForeignKey(
        RestaurantTable, on_delete=models.SET_NULL, db_index=True, null=True
    )
    created_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        db_index=True,
        null=True,
        help_text=_("The user that initialed the order."),
    )
    participants = models.ManyToManyField(
        User, help_text=_("Total participants of this order.")
    )
    created_at = models.DateTimeField(auto_now_add=True)

    def get_total(self) -> Decimal:
        """
        calculates orders total amount to be paid.
        """
        total = 0.0
        items = OrderItem.objects.filter(order=self)
        for i in items:
            add_ons = OrderItemAddOn.objects.filter(order_item=i)
            for a in add_ons:
                total += (
                    a.food_add_on.price * a.quantity * i.quantity
                )  # Number of add on * Number of item * price of add ons
            total += i.food_item.price * i.quantity
        return Decimal(total)

    def get_total_of_user(self, user: User) -> Decimal:
        """
        Get total payable by each user.
        """
        total = 0.0
        order_items = OrderItem.objects.filter(order=self)
        items = order_items.filter(Q(added_by=user) | Q(shared_with__exact=user))
        for i in items:
            add_ons = OrderItemAddOn.objects.filter(order_item=i)
            for a in add_ons:
                total += (
                    a.food_add_on.price * a.quantity * i.quantity
                )  # Number of add on * Number of item * price of add ons
            total += i.food_item.price * i.quantity
        return Decimal(total)


class OrderInvite(models.Model):
    STATUSES = ((0, _("Pending")), (1, _("Accepted")), (2, _("Rejected")))
    order = models.ForeignKey(
        Order,
        on_delete=models.SET_NULL,
        db_index=True,
        related_name="restaurant_order_invites",
        null=True,
    )
    invited_user = models.ForeignKey(User, on_delete=models.CASCADE, db_index=True)
    invited_by = models.ForeignKey(User, on_delete=models.CASCADE, db_index=True)
    status = models.SmallIntegerField()
    created_at = models.DateTimeField(auto_now_add=True)

    @staticmethod
    def can_send_invite(from_user: User, to_user: User, order: Order) -> bool:
        max_number = settings.MAX_NUMBER_OF_ORDER_INVITE_TRY
        return (
            OrderInvite.objects.filter(
                invited_user=to_user, invited_by=from_user, order=order
            ).count()
            <= max_number
        )


class OrderItem(models.Model):
    STATUS_CHOICES = ((0, _("Unconfirmed")), (1, _("Confirmed")), (2, _("Canceled")))
    food_item = models.ForeignKey(FoodItem, on_delete=models.SET_NULL, null=True)
    quantity = models.PositiveIntegerField(default=1)
    order = models.ForeignKey(
        Order, on_delete=models.CASCADE, related_name="order_items"
    )
    status = models.SmallIntegerField(choices=STATUS_CHOICES, default=0, db_index=True)
    shared_with = models.ManyToManyField(User)
    added_by = models.ForeignKey(
        User, on_delete=models.SET_NULL, null=True, db_index=True
    )
    attributes = models.ManyToManyField(FoodAttributeMatrix)
    created_at = models.DateTimeField(auto_now_add=True)

    def get_total(self) -> Decimal:
        """
        calculates items total amount to be paid.
        """
        total = 0.0
        add_ons = OrderItemAddOn.objects.filter(order_item=self)
        for a in add_ons:
            total += (
                a.food_add_on.price * a.quantity * self.quantity
            )  # Number of add on * Number of item * price of add ons
        total += self.food_item.price * self.quantity
        return Decimal(total)


class OrderItemAddOn(models.Model):
    food_add_on = models.ForeignKey(FoodAddOn, on_delete=models.SET_NULL, null=True)
    quantity = models.PositiveIntegerField(default=1)
    order_item = models.ForeignKey(
        OrderItem, on_delete=models.CASCADE, related_name="order_item_add_ons"
    )
    created_at = models.DateTimeField(auto_now_add=True)
