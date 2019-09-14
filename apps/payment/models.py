from django.db import models
from apps.order.models import Order


class Invoice(models.Model):
    amount = models.DecimalField(max_digits=9, decimal_places=2)
    order = models.ForeignKey(Order, on_delete=models.CASCADE, db_index=True, related_name="invoice")
    created_at = models.DateTimeField(auto_now_add=True)

