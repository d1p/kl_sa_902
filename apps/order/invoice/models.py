import string
from decimal import Decimal
from secrets import choice

from django.db import models
from django.utils.translation import ugettext_lazy as _

from apps.account.models import User
from apps.order.invoice.types import PaymentStatus
from apps.order.models import Order, OrderItem
from apps.order.types import OrderItemStatusType


class Invoice(models.Model):
    order = models.OneToOneField(Order, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)

    def generate_invoice_items(self):
        order: Order = self.order
        participants = order.order_participants.all()
        for participant in participants:
            ordered_items = OrderItem.objects.filter(
                order=order,
                shared_with=participant.user,
                status=OrderItemStatusType.CONFIRMED,
            )
            if ordered_items.count() > 0:
                price = order.get_total_of_user(participant.user)
                tax = order.get_total_tax_of_user(participant.user)
                amount = price + tax
                InvoiceItem.objects.create(
                    invoice=self,
                    user=participant.user,
                    general_amount=price,
                    tax_amount=tax,
                    amount=amount,
                )


class InvoiceItem(models.Model):
    invoice = models.ForeignKey(
        Invoice, on_delete=models.CASCADE, related_name="invoice_items"
    )
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    general_amount = models.DecimalField(
        decimal_places=3,
        max_digits=9,
        default=Decimal(0),
        help_text=_("Actual price of the items, without Tax."),
    )
    tax_amount = models.DecimalField(
        decimal_places=3,
        max_digits=9,
        default=Decimal(0),
        help_text=_("Total payable tax amount."),
    )
    amount = models.DecimalField(
        decimal_places=3,
        max_digits=9,
        help_text=_("Actual amount that the user has to pay. With taxing."),
    )
    paid = models.BooleanField(default=False, db_index=True)

    @property
    def food_items(self) -> []:
        ordered_items = OrderItem.objects.filter(
            order=self.invoice.order,
            shared_with=self.user,
            status=OrderItemStatusType.CONFIRMED,
        )

        return ordered_items

    @property
    def successful_transactions(self) -> []:
        return Transaction.objects.filter(
            order=self, transaction_status=PaymentStatus.SUCCESSFUL
        )


class Transaction(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    order = models.ForeignKey(Order, on_delete=models.CASCADE)
    invoice_items = models.ManyToManyField(InvoiceItem)

    transaction_status = models.IntegerField(
        choices=PaymentStatus.CHOICES, default=PaymentStatus.PENDING, db_index=True
    )

    pt_order_id = models.CharField(max_length=32, unique=True)
    pt_transaction_id = models.CharField(
        max_length=12, unique=True, null=True, blank=True
    )
    currency = models.CharField(max_length=3, default="SAR")
    amount = models.DecimalField(max_digits=10, decimal_places=3)

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = _("Transaction")
        verbose_name_plural = _("Transactions")

    def save(self, *args, **kwargs):
        if self.pk is None:
            self.pt_order_id = generate_order_id(self.user.id)
        super(Transaction, self).save(*args, **kwargs)


def generate_order_id(user_id: int) -> str:
    max_length = 32
    user_id_length = len(str(user_id))
    alphabet = string.ascii_letters + string.digits
    secret = "".join(choice(alphabet) for i in range(max_length - user_id_length))
    order_id = f"{user_id}{secret}"
    if Transaction.objects.filter(pt_order_id=order_id).exists():
        return generate_order_id(user_id)  # pragma: no cover
    else:
        return order_id
