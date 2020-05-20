from decimal import Decimal

from django.conf import settings
from django.db import models
from django.db.models import Avg
from django.db.models import F
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
from ..notification.models import Action


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
        RestaurantTable, on_delete=models.SET_NULL, db_index=True, null=True, blank=True
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

    has_restaurant_accepted = models.BooleanField(null=True, blank=True, default=None)

    payment_completed = models.BooleanField(default=False, db_index=True)

    confirmed = models.BooleanField(
        default=False,
        db_index=True,
        help_text=_("Indicated if an order is confirmed by the users"),
    )

    tax_percentage = models.DecimalField(max_digits=6, decimal_places=2, default=0.00)

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ("-id",)

    def __str__(self):
        return str(self.id)

    @property
    def table_name(self):
        if self.table:
            return self.table_name
        return None

    def is_active(self) -> bool:
        return (
            OrderItem.objects.filter(
                order=self, status=OrderItemStatusType.CONFIRMED
            ).exists()
            and self.status == OrderStatusType.OPEN
        )

    def total_price_without_tax(self) -> Decimal:
        """
        calculates orders total amount to be paid.
        """
        total = Decimal(0.0)
        items = OrderItem.objects.filter(
            order=self, status=OrderItemStatusType.CONFIRMED
        )
        for i in items:
            total += i.total_price_without_tax()
        return Decimal(total)

    def total_price_with_tax(self) -> Decimal:
        total_with_tax = self.total_price_without_tax() + (
            self.total_price_without_tax()
            * Decimal(self.restaurant.restaurant.tax_percentage)
        ) / Decimal(100.00)
        return Decimal(total_with_tax)

    def shared_price_without_tax(self, user: User) -> Decimal:
        """
        Get total payable by each user.
        """
        total = Decimal(0.0)
        items = OrderItem.objects.filter(
            order=self, status=OrderItemStatusType.CONFIRMED, shared_with=user
        )

        for i in items:
            total += i.shared_price_without_tax()
        return Decimal(total)

    def shared_price_with_tax(self, user: User) -> Decimal:
        """
        Get total tax by each user
        """
        total = self.shared_price_without_tax(user) + (
            self.shared_price_without_tax(user) * Decimal(self.tax_percentage)
        ) / Decimal(100.00)
        return Decimal(total)

    def total_tax_amount(self) -> Decimal:
        return self.total_price_with_tax() - self.total_price_without_tax()

    def shared_tax_amount(self, user: User):
        return self.shared_price_with_tax(user) - self.shared_price_without_tax(user)


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
        choices=OrderInviteStatusType.CHOICES,
        default=OrderInviteStatusType.PENDING,
        help_text="PENDING = 0, ACCEPTED = 1, REJECTED = 2",
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

    def total_price_without_tax(self) -> Decimal:
        """
        calculates items total amount to be paid.
        """
        total = Decimal(0.0)
        add_ons = OrderItemAddOn.objects.filter(order_item=self)
        for a in add_ons:
            total += (
                a.food_add_on.price * Decimal(a.quantity) * Decimal(self.quantity)
            )  # Number of add on * Number of item * price of add ons
        total += self.food_item.price * Decimal(self.quantity)
        return total

    def total_price_with_tax(self) -> Decimal:
        return self.total_price_without_tax() + (
            self.total_price_without_tax()
            * Decimal(self.food_item.user.restaurant.tax_percentage)
        ) / Decimal(100.00)

    def shared_price_without_tax(self) -> Decimal:
        total = self.total_price_without_tax()
        try:
            return total / Decimal(self.shared_with.count())
        except ZeroDivisionError:
            return total

    def shared_price_with_tax(self) -> Decimal:
        total = self.total_price_with_tax()
        try:
            return total / Decimal(self.shared_with.count())
        except ZeroDivisionError:
            return total

    def total_tax(self):
        return self.total_price_with_tax() - self.total_price_without_tax()

    def shared_total_tax(self):
        return self.shared_price_with_tax() - self.shared_price_without_tax()


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
        OrderItem,
        related_name="order_item_attribute_matrices",
        on_delete=models.CASCADE,
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
        related_name="order_item_invites",
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


class Rating(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="rated_by")
    restaurant = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="rated_restaurant"
    )
    food_item_rating = models.PositiveSmallIntegerField(default=0)
    restaurant_rating = models.PositiveSmallIntegerField(default=0)
    customer_service_rating = models.PositiveSmallIntegerField(default=0)
    application_rating = models.PositiveSmallIntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.name} rated {self.restaurant.name}"

    @staticmethod
    def get_average_restaurant_rating(restaurant: User):
        rating = (
            Rating.objects.filter(restaurant=restaurant)
            .annotate(
                n_rating=F("food_item_rating")
                + F("restaurant_rating")
                + F("customer_service_rating")
                + F("application_rating")
            )
            .aggregate(avg_rating=Avg("n_rating"))
        )
        try:
            return Decimal(rating["avg_rating"] / 4)
        except (TypeError, ZeroDivisionError):
            return Decimal(0.00)
