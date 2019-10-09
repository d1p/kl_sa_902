from decimal import Decimal

from django.db import transaction
from rest_framework import serializers
from rest_framework.exceptions import ValidationError, PermissionDenied

from apps.account.models import User
from apps.account.serializers import PublicUserSerializer
from apps.order.invoice.tasks import (
    send_checkout_push_notification_to_other_users,
    send_checkout_push_notification_to_the_restaurant,
)
from apps.order.models import Order
from apps.order.types import OrderStatusType
from .models import Invoice, InvoiceItem, Transaction


class InvoiceItemSerializer(serializers.ModelSerializer):
    user = PublicUserSerializer(read_only=True)

    class Meta:
        model = InvoiceItem
        fields = ("id", "invoice", "user", "amount", "paid")
        read_only_fields = ("id", "invoice", "user", "amount", "paid")


class InvoiceSerializer(serializers.ModelSerializer):
    invoice_items = InvoiceItemSerializer(many=True, read_only=True)

    class Meta:
        model = Invoice
        fields = ("id", "order", "invoice_items", "created_at")
        read_only_fields = ("id", "created_at")

    def create(self, validated_data):
        current_user: User = self.context["request"].user
        order: Order = validated_data.get("order")
        if order.order_participants.filter(user=current_user).exists() is False:
            raise PermissionDenied

        if order.status != OrderStatusType.OPEN:
            raise ValidationError({"order": ["Order is not open."]})

        try:
            invoice = Invoice.objects.get(order=order)
        except Invoice.DoesNotExist:
            with transaction.atomic():
                invoice = Invoice.objects.create(**validated_data)
                invoice.generate_invoice_items()
                order.status = OrderStatusType.CHECKOUT
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


class TransactionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Transaction
        fields = (
            "id",
            "user",
            "invoice_items",
            "order",
            "pt_transaction_status",
            "pt_order_id",
            "transaction_id",
            "currency",
            "amount",
            "created_at",
        )
        read_only_fields = (
            "id",
            "user",
            "order_id",
            "transaction_id",
            "currency",
            "amount",
            "created_at",
        )

    def create(self, validated_data):
        order: Order = validated_data.get("order")
        if (
            order.order_participants.filter(user=validated_data.get("user")).exists()
            is False
        ):
            raise PermissionDenied

        amount: Decimal = Decimal(0.0)

        for invoice_item in validated_data.get("invoice_items"):
            if invoice_item.order != order:
                raise PermissionDenied
            if invoice_item.paid is True:
                raise ValidationError(
                    {"invoice_items": [f"Item {invoice_item.id} has been paid."]}
                )
            amount += invoice_item.amount

        instance = Transaction.objects.create(**validated_data)
        return instance


class TransactionVerifySerializer(serializers.Serializer):
    transaction_id = serializers.CharField(required=True)
