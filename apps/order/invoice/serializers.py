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
from ..serializers import OrderItemSerializer


class InvoiceItemSerializer(serializers.ModelSerializer):
    user = PublicUserSerializer(read_only=True)
    food_items = OrderItemSerializer(many=True, read_only=True)

    class Meta:
        model = InvoiceItem
        fields = (
            "id",
            "invoice",
            "user",
            "general_amount",
            "tax_amount",
            "amount",
            "paid",
            "food_items",
        )
        read_only_fields = (
            "id",
            "invoice",
            "user",
            "amount",
            "general_amount",
            "tax_amount",
            "paid",
        )


class InvoiceSerializer(serializers.ModelSerializer):
    invoice_items = InvoiceItemSerializer(many=True, read_only=True)
    restaurant_name = serializers.CharField(
        source="order.restaurant.name", read_only=True
    )
    restaurant_address = serializers.CharField(
        source="order.restaurant.Restaurant.full_address", read_only=True
    )

    class Meta:
        model = Invoice
        fields = (
            "id",
            "order",
            "invoice_items",
            "restaurant_name",
            "restaurant_address",
            "created_at",
        )
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
                for p in order.order_participants.all():
                    p.user.misc.set_order_in_checkout()

            # Send necessary Signals.
            send_checkout_push_notification_to_other_users(
                from_user=current_user.id, order_id=order.id
            )
            send_checkout_push_notification_to_the_restaurant(order_id=order.id)
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
            "transaction_status",
            "pt_order_id",
            "pt_transaction_id",
            "currency",
            "amount",
            "created_at",
        )
        read_only_fields = (
            "id",
            "user",
            "transaction_status",
            "pt_order_id",
            "pt_transaction_id",
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
        invoice_items = validated_data.pop("invoice_items")
        for invoice_item in invoice_items:
            if invoice_item.invoice.order != order:
                raise PermissionDenied
            if invoice_item.paid is True:
                raise ValidationError(
                    {"invoice_items": [f"Item {invoice_item.id} has been paid."]}
                )
            amount += invoice_item.amount
        instance = Transaction.objects.create(
            order=order, user=validated_data.get("user"), amount=amount
        )
        for invoice_item in invoice_items:
            instance.invoice_items.add(invoice_item)
        instance.refresh_from_db()

        return instance


class TransactionVerifySerializer(serializers.Serializer):
    transaction_id = serializers.CharField(required=True)
