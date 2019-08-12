from rest_framework import serializers
from rest_framework.exceptions import PermissionDenied, ValidationError

from apps.account.serializers import PublicUserSerializer
from .models import Ticket, Message, PreBackedTicketTopic


class PreBackedTicketTopicSerializer(serializers.ModelSerializer):
    class Meta:
        model = PreBackedTicketTopic
        fields = ("text", "text_in_ar")


class TicketSerializer(serializers.ModelSerializer):
    created_by = PublicUserSerializer(required=False)

    class Meta:
        model = Ticket
        fields = ("id", "created_by", "topic", "description", "status")
        read_only_fields = ("id", "created_at", "created_by", "status")


class MessageSerializer(serializers.ModelSerializer):
    sender = PublicUserSerializer(read_only=True)

    class Meta:
        model = Message
        fields = ("id", "sender", "ticket", "text", "created_at")
        read_only_fields = ("id", "sender", "ticket", "created_at")

    def create(self, validated_data):
        sender = validated_data.get("sender")
        ticket = validated_data.get("ticket")

        if sender.is_staff is False and sender.id != ticket.created_by.id:
            raise PermissionDenied

        if ticket.status == Ticket.CLOSED:
            raise ValidationError(
                {"non_field_errors": ["This ticket has been closed."]}
            )

        return Message.objects.create(**validated_data)
