from rest_framework import serializers
from rest_framework.exceptions import ValidationError, PermissionDenied

from apps.account.serializers import PrivateUserSerializer
from apps.food.serializers import FoodAttributeMatrixSerializer, FoodAddOnSerializer
from apps.order.types import OrderStatusType, OrderInviteStatusType
from .models import (
    Order,
    OrderInvite,
    OrderItem,
    OrderItemInvite,
    OrderParticipant,
    OrderItemAddOn,
    OrderItemAttributeMatrix,
)


class BulkOrderInviteSerializer(serializers.Serializer):
    invited_users = serializers.ListField(child=serializers.IntegerField())
    order = serializers.IntegerField()

    def create(self, validated_data):
        pass

    def update(self, instance, validated_data):
        pass


class OrderInviteSerializer(serializers.ModelSerializer):
    class Meta:
        model = OrderInvite
        fields = ("invited_user", "order", "status")
        read_only_fields = ("id", "invited_by", "created_at")

    def update(self, instance: OrderInvite, validated_data):
        """
        Update should only be used by the invited user to accept or reject the request.
        """
        current_user = self.context["request"].user
        if instance.invited_user != current_user or instance.status != 0:
            raise PermissionDenied
        print(validated_data)
        if validated_data.get("status") == 1:
            # Accepts
            order = instance.order
            order.order_participants.create(user=current_user)
            current_user.misc.last_order = order
            current_user.misc.save()
            instance.status = OrderInviteStatusType.ACCEPTED
            instance.save()
            # Send necessary signals
        else:
            instance.status = OrderInviteStatusType.REJECTED
            instance.save()

        return instance


class BulkOrderItemInviteSerializer(serializers.Serializer):
    invited_users = serializers.ListField(child=serializers.IntegerField())
    order_item = serializers.IntegerField()

    def create(self, validated_data):
        pass

    def update(self, instance, validated_data):
        pass


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


class OrderItemAddOnSerializer(serializers.ModelSerializer):
    food_add_on_details = FoodAddOnSerializer(source="food_add_on", read_only=True)

    class Meta:
        model = OrderItemAddOn
        fields = ("id", "food_add_on", "food_add_on_details", "created_at")
        read_only_fields = ("id", "food_add_on_details", "created_at")


class OrderItemAttributeMatrixSerializer(serializers.ModelSerializer):
    food_attribute_matrix_details = FoodAttributeMatrixSerializer(
        source="food_attribute_matrix", read_only=True
    )

    class Meta:
        model = OrderItemAttributeMatrix
        fields = (
            "id",
            "food_attribute_matrix",
            "food_attribute_matrix_details",
            "created_at",
        )
        read_only_fields = ("id", "food_attribute_matrix_details", "created_at")


class OrderItemSerializer(serializers.ModelSerializer):
    order_item_add_ons = OrderItemAddOnSerializer(many=True, required=False)
    order_item_attribute_matrices = OrderItemAttributeMatrixSerializer(
        many=True, required=False
    )

    class Meta:
        model = OrderItem
        fields = (
            "id",
            "order",
            "food_item",
            "quantity",
            "order_item_add_ons",
            "order_item_attribute_matrices",
            "status",
            "shared_with",
            "added_by",
            "created_at",
        )
        read_only_fields = ("id", "added_by", "shared_with", "created_at")

    def create(self, validated_data):
        order = validated_data.get("order")

        if order.status == OrderStatusType.OPEN:
            order_item_addons = validated_data.pop("order_item_add_ons")
            order_item_attribute_matrices = validated_data.pop(
                "order_item_attribute_matrices"
            )

            order_item = OrderItem.objects.create(**validated_data)

            for order_addon in order_item_addons:
                add_on = order_addon["food_add_on"]
                if (
                    OrderItemAddOn.objects.filter(
                        order_item=order_item, food_add_on=add_on
                    ).exists()
                    is False
                ):
                    OrderItemAddOn.objects.create(
                        order_item=order_item, food_add_on=add_on
                    )

            for order_attribute_matrix in order_item_attribute_matrices:
                attribute_matrix = order_attribute_matrix["food_attribute_matrix"]
                if (
                    OrderItemAttributeMatrix.objects.filter(
                        order_item=order_item, food_attribute_matrix=attribute_matrix
                    ).exists()
                    is False
                ):
                    OrderItemAttributeMatrix.objects.create(
                        order_item=order_item, food_attribute_matrix=attribute_matrix
                    )
            order_item.refresh_from_db()
            return order_item
        else:
            return ValidationError(
                {"non_field_errors": ["This order has been closed."]}
            )


class OrderParticipantSerializer(serializers.ModelSerializer):
    user = PrivateUserSerializer()

    class Meta:
        model = OrderParticipant
        fields = ("user", "created_at", "order")


class OrderSerializer(serializers.ModelSerializer):
    order_participants = OrderParticipantSerializer(
        required=False, read_only=True, many=True
    )

    class Meta:
        model = Order
        fields = (
            "id",
            "order_type",
            "restaurant",
            "table",
            "order_item_set",
            "order_participants",
            "created_by",
            "created_at",
        )
        read_only_fields = ("id", "created_by", "created_at", "order_item_set")

    def create(self, validated_data):
        order = Order.objects.create(**validated_data)
        order.order_participants.create(user=order.created_by)
        order.created_by.misc.last_order = order
        order.created_by.misc.save()
        return order


class ConfirmSerializer(serializers.Serializer):
    sure = serializers.BooleanField(required=True)
