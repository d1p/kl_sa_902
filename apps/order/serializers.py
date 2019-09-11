from rest_framework import serializers
from rest_framework.exceptions import ValidationError, PermissionDenied

from .models import Order, OrderInvite, OrderParticipant


class OrderInviteSerializer(serializers.ModelSerializer):
    class Meta:
        model = OrderInvite
        fields = ("id", "invited_user", "invited_by", "status", "created_at")
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
            OrderParticipant.objects.create(order=order, user=current_user)
            instance.status = 1
            instance.save()
            # Send necessary signals
        else:
            instance.status = 2
            instance.save()

        return instance


class OrderSerializer(serializers.ModelSerializer):
    class Meta:
        model = Order
        fields = ("id", "order_type", "restaurant", "table", "created_by", "created_at")
