from django.db import transaction
from rest_framework import serializers
from rest_framework.exceptions import ValidationError

from apps.account.models import User
from apps.order.invoice.tasks import (
    send_checkout_push_notification_to_other_users,
    send_checkout_push_notification_to_the_restaurant,
)
from apps.order.models import Order
from apps.order.types import OrderStatusType
from .models import Invoice


class InvoiceSerializer(serializers.ModelSerializer):
    class Meta:
        model = Invoice
        fields = ("id", "order", "created_at")
        read_only_fields = ("id", "created_at")

    def create(self, validated_data):
        current_user: User = self.context["request"].user
        order: Order = validated_data.get("order")
        if order.status != OrderStatusType.OPEN:
            raise ValidationError({"order": ["Order is not open."]})
        with transaction.atomic():
            invoice = Invoice.objects.create(**validated_data)
            order.status = OrderStatusType.COMPLETED
            order.save()

        # Send necessary Signals.
        send_checkout_push_notification_to_other_users(
            from_user=current_user.id, order_id=order.id
        )
        send_checkout_push_notification_to_the_restaurant(
            from_user=current_user.id, order_id=order.id
        )
        invoice.refresh_from_db()

        return invoice
