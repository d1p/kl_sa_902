from rest_framework import serializers

from .models import Action


class ActionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Action
        fields = (
            "id",
            "sender_name",
            "message",
            "action_type",
            "message_in_ar",
            "created_at",
            "extra_data",
        )


class OrderRemainingTimeNotificationSerializer(serializers.Serializer):
    order_id = serializers.IntegerField(required=True)
    remaining_time = serializers.IntegerField(required=True)


class ConfirmSerializer(serializers.Serializer):
    sure = serializers.BooleanField(required=True)
