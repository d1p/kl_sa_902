from rest_framework import serializers
from rest_framework.exceptions import ValidationError, PermissionDenied

from apps.account.models import User
from apps.account.serializers import PrivateUserSerializer
from apps.contact.models import ContactGroup
from apps.order.tasks import send_order_invite_notification
from apps.order.types import OrderStatusType
from .models import Order, OrderInvite, OrderItem, OrderItemInvite, OrderParticipant


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
            invite = OrderInvite.objects.create(**validated_data, status=0)
            send_order_invite_notification(
                from_user=validated_data.get("invited_by"),
                to_user=validated_data.get("invited_user"),
                invite_id=invite.id,
            )
            return invite

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
        read_only_fields = ("id", "created_by", "created_at")

    def create(self, validated_data):
        order = Order.objects.create(**validated_data)
        order.order_participants.create(user=order.created_by)
        return order


class OrderGroupInviteSerializer(serializers.Serializer):
    group_id = serializers.IntegerField(required=True)
    order_id = serializers.IntegerField(required=True)

    def create(self, validated_data):
        current_user: User = self.context["request"].user

        try:
            order = Order.objects.get(id=validated_data.get("order_id"))
        except Order.DoesNotExist:
            raise ValidationError({"id": ["Invalid order id"]})

        if order.user != current_user:
            raise PermissionDenied

        try:
            contact_group = ContactGroup.objects.get(id=validated_data.get("group_id"))
        except ContactGroup.DoesNotExist:
            raise ValidationError({"id": ["Invalid group id"]})

        if contact_group.user != current_user:
            raise PermissionDenied

        order_participants = order.order_participants.all().only("user")
        order_participants_users = [x.user for x in order_participants]

        for contact in contact_group.contacts:
            if contact not in order_participants_users:
                invite = OrderInvite.objects.create(
                    order=order, invited_user=contact, invited_by=current_user, status=0
                )
                send_order_invite_notification(
                    from_user=current_user, to_user=contact, invite_id=invite.id
                )

    def update(self, instance, validated_data):
        pass


class OrderParticipantSerializer(serializers.ModelSerializer):
    user = PrivateUserSerializer()

    class Meta:
        model = OrderParticipant
        fields = ("user", "created_at")
