from django.db import models
from apps.order.models import Order, OrderItem


class Invoice(models.Model):
    order = models.OneToOneField(Order, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)

class InvoiceItem(models.Model):
    invoice = models.ForeignKey(Invoice, on_delete=models.CASCADE)

