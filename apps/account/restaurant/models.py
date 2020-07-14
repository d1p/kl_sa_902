from decimal import Decimal

from django.contrib.gis.db.models import PointField
from django.contrib.gis.geos import Point
from django.db import models
from django.utils.translation import ugettext_lazy as _

from apps.account.models import User
from apps.order.invoice.types import PaymentStatus
from apps.order.types import OrderType, OrderStatusType
from utils.file import RandomFileName
from django.db.models import Sum


class Category(models.Model):
    name = models.CharField(max_length=45, unique=True, db_index=True)
    name_in_ar = models.CharField(
        _("Name in Arabic"), max_length=45, unique=True, db_index=True
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = _("Category")
        verbose_name_plural = _("Categories")

    def __str__(self):
        return f"{self.name} {self.name_in_ar}"


class Restaurant(models.Model):
    user = models.OneToOneField(User, db_index=True, on_delete=models.CASCADE)
    cover_picture = models.ImageField(
        upload_to=RandomFileName("user/restaurant/cover/"),
        default="user/restaurant/cover/default.png",
    )
    restaurant_type = models.ForeignKey(
        Category, on_delete=models.SET_NULL, null=True, blank=True, db_index=True
    )
    full_address = models.TextField(max_length=800, db_index=True, blank=True)
    geolocation = PointField(
        spatial_index=True, srid=4326, null=True, blank=True, editable=False
    )  # Srid 4326 is compatible with google maps.

    lat = models.FloatField(null=True, blank=True)
    lng = models.FloatField(null=True, blank=True)

    online = models.BooleanField(default=False, db_index=True)

    is_public = models.BooleanField(default=False, db_index=True)

    # payables
    pickup_order_cut = models.DecimalField(
        max_digits=12, decimal_places=3, default=100.00
    )
    inhouse_order_cut = models.DecimalField(
        max_digits=12, decimal_places=3, default=100.00
    )

    tax_percentage = models.DecimalField(max_digits=12, decimal_places=2, default=0.00)

    pickup_earning = models.DecimalField(max_digits=12, decimal_places=3, default=0.00)
    inhouse_earning = models.DecimalField(max_digits=12, decimal_places=3, default=0.00)

    app_pickup_earning = models.DecimalField(
        max_digits=12, decimal_places=3, default=0.0
    )

    app_inhouse_earning = models.DecimalField(
        max_digits=12, decimal_places=3, default=0.0
    )

    total_earning = models.DecimalField(max_digits=12, decimal_places=3, default=0.00)
    app_total_earning = models.DecimalField(
        max_digits=12, decimal_places=3, default=0.00
    )

    total = models.DecimalField(max_digits=12, decimal_places=3, default=0.0)

    def __str__(self):
        return f"{self.user} - {self.user.name}"

    def clean(self):
        if self.lat and self.lng:
            self.geolocation = Point(self.lng, self.lat, srid=4326)

    def rating(self):
        from apps.order.models import Rating

        rate = Rating.get_average_restaurant_rating(restaurant=self.user)
        return rate

    def total_orders(self) -> int:
        from apps.order.models import Order

        return Order.objects.filter(
            restaurant=self.user, status=OrderStatusType.COMPLETED
        ).count()

    def get_total_order_amount(self):
        from apps.order.invoice.models import InvoiceItem

        items = InvoiceItem.objects.filter(
            invoice__order__restaurant=self.user,
            invoice__order__status=OrderStatusType.COMPLETED,
        ).aggregate(Sum("amount"))

        amount = items["amount__sum"] if items is not None else Decimal(0.0)
        return amount

    def get_inhouse_earning(self) -> Decimal:
        from apps.order.invoice.models import Transaction

        total = Decimal(0)

        transactions = Transaction.objects.filter(
            order__restaurant=self.user,
            transaction_status=PaymentStatus.SUCCESSFUL,
            order__order_type=OrderType.IN_HOUSE,
        )

        for t in transactions:
            total += (t.amount / Decimal(100)) * t.order.invoice.order_cut
        return total

    def get_pickup_earning(self) -> Decimal:
        from apps.order.invoice.models import Transaction

        total = Decimal(0)

        transactions = Transaction.objects.filter(
            order__restaurant=self.user,
            transaction_status=PaymentStatus.SUCCESSFUL,
            order__order_type=OrderType.PICK_UP,
        )

        for t in transactions:
            total += (t.amount / Decimal(100)) * t.order.invoice.order_cut
        return total

    def get_total_earning(self) -> Decimal:
        return self.get_inhouse_earning() + self.get_pickup_earning()


class Payable(Restaurant):
    class Meta:
        proxy = True
        verbose_name = _("Restaurant Commission and Earning")
        verbose_name_plural = _("Restaurant Commissions and Earnings")


class RestaurantTable(models.Model):
    user = models.ForeignKey(User, db_index=True, on_delete=models.CASCADE)
    name = models.CharField(max_length=100)
    qr_code = models.ImageField(upload_to=RandomFileName("user/restaurant/table"))
    public = models.BooleanField(default=True, db_index=True)
    created_at = models.DateTimeField(auto_now_add=True)
    is_active = models.BooleanField(default=True, db_index=True)

    def __str__(self):
        return f"{self.name} by {self.user.name}"
