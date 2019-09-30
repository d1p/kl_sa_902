from decimal import Decimal

from django.conf import settings
from django.db import models
from django.db.models import Q
from django.utils.translation import ugettext_lazy as _

from apps.account.models import User
from apps.account.restaurant.models import RestaurantTable
from apps.food.models import FoodItem, FoodAddOn, FoodAttributeMatrix
from .types import (
    OrderType,
    OrderItemStatusType,
    OrderStatusType,
    OrderInviteStatusType,
)


class Order(models.Model):
    order_type = models.SmallIntegerField(
        choices=OrderType.CHOICES,
        help_text=_(
            "Indicates weather the order is a Pick up (0) order or In House (1)"
        ),
    )
    restaurant = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        db_index=True,
        null=True,
        related_name="order_restaurants",
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

    status = models.SmallIntegerField(
        choices=OrderStatusType.CHOICES, default=OrderStatusType.OPEN
    )

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return str(self.id)

    def is_active(self) -> bool:
        return (
            OrderItem.objects.filter(
                order=self, status=OrderItemStatusType.CONFIRMED
            ).exists()
            and self.status == OrderStatusType.OPEN
        )

    def get_total(self) -> Decimal:
        """
        calculates orders total amount to be paid.
        """
        total = 0.0
        items = OrderItem.objects.filter(order=self)
        for i in items:
            add_ons = OrderItemAddOn.objects.filter(
                order_item=i, order_item__status=OrderItemStatusType.CONFIRMED
            )
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
        order_items = OrderItem.objects.filter(
            order=self, order_item__status=OrderItemStatusType.CONFIRMED
        )
        items = order_items.filter(Q(added_by=user) | Q(shared_with__exact=user))
        for i in items:
            add_ons = OrderItemAddOn.objects.filter(order_item=i)
            for a in add_ons:
                total += (
                    a.food_add_on.price * a.quantity * i.quantity
                )  # Number of add on * Number of item * price of add ons
            total += i.food_item.price * i.quantity
        return Decimal(total)


class OrderParticipant(models.Model):
    order = models.ForeignKey(
        Order, related_name="order_participants", on_delete=models.CASCADE
    )
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    created_at = models.DateTimeField(auto_now_add=True)


class OrderInvite(models.Model):
    order = models.ForeignKey(
        Order,
        on_delete=models.SET_NULL,
        db_index=True,
        related_name="restaurant_order_invites",
        null=True,
    )
    invited_user = models.ForeignKey(
        User, on_delete=models.CASCADE, db_index=True, related_name="order_invited_user"
    )
    invited_by = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        db_index=True,
        related_name="order_invited_by_user",
    )

    status = models.SmallIntegerField(
        choices=OrderInviteStatusType.CHOICES, default=OrderInviteStatusType.PENDING,
        help_text="PENDING = 0, ACCEPTED = 1, REJECTED = 2"
    )

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
    food_item = models.ForeignKey(FoodItem, on_delete=models.SET_NULL, null=True)

    quantity = models.PositiveIntegerField(default=1)
    order = models.ForeignKey(
        Order, on_delete=models.CASCADE, related_name="order_item_set"
    )
    status = models.SmallIntegerField(
        choices=OrderItemStatusType.CHOICES,
        default=OrderItemStatusType.UNCONFIRMED,
        db_index=True,
    )
    shared_with = models.ManyToManyField(
        User, related_name="order_item_shared_with_users"
    )
    added_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        db_index=True,
        related_name="order_item_added_by_user",
    )
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


class OrderItemAttributeMatrix(models.Model):
    food_attribute_matrix = models.ForeignKey(
        FoodAttributeMatrix, on_delete=models.CASCADE, null=True
    )
    order_item = models.ForeignKey(
        OrderItem, related_name="order_item_attribute_matrix", on_delete=models.CASCADE
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ("order_item", "food_attribute_matrix")


class OrderItemInvite(models.Model):
    STATUSES = ((0, _("Pending")), (1, _("Accepted")), (2, _("Rejected")))
    order_item = models.ForeignKey(
        OrderItem,
        on_delete=models.SET_NULL,
        db_index=True,
        related_name="restaurant_order_item_invites",
        null=True,
    )
    invited_user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        db_index=True,
        related_name="order_item_invited_user",
    )
    invited_by = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        db_index=True,
        related_name="order_item_invited_by_user",
    )

    status = models.SmallIntegerField(choices=STATUSES, default=0)

    created_at = models.DateTimeField(auto_now_add=True)

    @staticmethod
    def can_send_invite(to_user: User, order_item: OrderItem) -> bool:
        return (
            order_item.order.order_participants.filter(id=to_user).exists()
            and order_item.shared_with.filter(id=to_user).exists() is False
        )
