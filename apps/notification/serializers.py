from rest_framework import serializers

from .models import Action


class ActionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Action
        fields = (
            "id",
            "sender_name",
            "sender_picture",
            "message",
            "action_type",
            "message_in_ar",
            "created_at",
            "extra_data",
        )
