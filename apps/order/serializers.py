from rest_framework import serializers
from rest_framework.exceptions import ValidationError, PermissionDenied

from apps.order.types import OrderStatusType
from .models import Order, OrderInvite, OrderItem, OrderItemInvite


class OrderInviteSerializer(serializers.ModelSerializer):
    class Meta:
        model = OrderInvite
        fields = ("id", "invited_user", "invited_by", "order", "status", "created_at")
        read_only_fields = ("id", "invited_by", "status", "created_at")

    def create(self, validated_data):
        if (
            OrderInvite.can_send_invite(
                from_user=validated_data.get("invited_by"),
                to_user=validated_data.get("invited_user"),
                order=validated_data.get("order"),
            )
            is False
        ):
            raise ValidationError(
                {"non_field_errors": ["Maximum number of invite exceeded."]}
            )
        else:
            return OrderInvite.objects.create(**validated_data, status=0)

    def update(self, instance: OrderInvite, validated_data):
        """
        Update should only be used by the invited user to accept or reject the request.
        """
        current_user = self.context["request"].user
        if instance.invited_user != current_user or instance.status != 0:
            raise PermissionDenied

        if validated_data.get("status") == 1:
            # Accepts
            order = instance.order
            order.order_participants.add(current_user)
            instance.status = 1
            instance.save()
            # Send necessary signals
        else:
            instance.status = 2
            instance.save()

        return instance


class OrderItemInviteSerializer(serializers.ModelSerializer):
    class Meta:
        model = OrderItemInvite
        fields = (
            "id",
            "invited_user",
            "invited_by",
            "order_item",
            "status",
            "created_at",
        )
        read_only_fields = ("id", "invited_by", "status", "created_at")

    def create(self, validated_data):
        if (
            OrderItemInvite.can_send_invite(
                to_user=validated_data.get("invited_user"),
                order_item=validated_data.get("order_item"),
            )
            is False
        ):
            raise ValidationError({"invited_user": ["User can not be invited."]})
        else:
            return OrderItemInvite.objects.create(**validated_data, status=0)

    def update(self, instance: OrderItemInvite, validated_data):
        """
        Update should only be used by the invited user to accept or reject the request.
        """
        current_user = self.context["request"].user
        if instance.invited_user != current_user or instance.status != 0:
            raise PermissionDenied

        if validated_data.get("status") == 1:
            # Accepts
            order_item = instance.order_item
            order_item.shared_with.add(current_user)
            instance.status = 1
            instance.save()
            # Send necessary signals
        else:
            instance.status = 2
            instance.save()

        return instance


class OrderItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = OrderItem
        fields = (
            "id",
            "food_item",
            "quantity",
            "status",
            "shared_with",
            "added_by",
            "created_at",
        )
        read_only_fields = ("id", "added_by", "created_at")

    def create(self, validated_data):
        order = validated_data.get("order")

        if order.status == OrderStatusType.OPEN:
            return Order.objects.create(**validated_data)
        else:
            return ValidationError(
                {"non_field_errors": ["This order has been closed."]}
            )


class OrderSerializer(serializers.ModelSerializer):
    class Meta:
        model = Order
        fields = ("id", "order_type", "restaurant", "table", "created_by", "created_at")
