from rest_framework import serializers
from rest_framework.exceptions import PermissionDenied, ValidationError

from apps.account.serializers import PublicUserSerializer
from .models import (
    RestaurantTicket,
    RestaurantMessage,
    PreBackedTicketTopic,
    ReportIssue,
    CustomerTicketTopic,
    CustomerTicket)
from .tasks import send_message_notification


class PreBackedTicketTopicSerializer(serializers.ModelSerializer):
    class Meta:
        model = PreBackedTicketTopic
        fields = ("text", "text_in_ar")


class CustomerTicketTopicSerializer(serializers.ModelSerializer):
    class Meta:
        model = CustomerTicketTopic
        fields = ("id", "text", "text_in_ar")


class CustomerTicketSerializer(serializers.ModelSerializer):
    created_by = PublicUserSerializer(required=False)

    class Meta:
        model = CustomerTicket
        fields = ("id", "created_by", "topic", "sub_topic", "description")
        read_only_fields = ("id", "created_at", "created_by")


class ReportIssueSerializer(serializers.ModelSerializer):
    class Meta:
        model = ReportIssue
        fields = ("created_by", "order", "topic", "description")
        read_only_fields = ("created_by",)

    def create(self, validated_data):
        if (
            validated_data.get("order")
            .order_participants.filter(user=validated_data.get("created_by"))
            .exists()
            is False
        ):
            raise PermissionDenied
        return ReportIssue.objects.create(
            created_by=validated_data.get("created_by"),
            topic=validated_data.get("topic"),
            order=validated_data.get("order"),
            description=validated_data.get("description"),
        )


class RestaurantTicketSerializer(serializers.ModelSerializer):
    created_by = PublicUserSerializer(required=False)

    class Meta:
        model = RestaurantTicket
        fields = ("id", "created_by", "topic", "description", "status", "created_at")
        read_only_fields = ("id", "created_at", "created_by", "status")


class RestaurantMessageSerializer(serializers.ModelSerializer):
    sender = PublicUserSerializer(read_only=True)

    class Meta:
        model = RestaurantMessage
        fields = ("id", "sender", "ticket", "text", "created_at")
        read_only_fields = ("id", "sender", "ticket", "created_at")

    def create(self, validated_data):
        sender = validated_data.get("sender")
        ticket = validated_data.get("ticket")

        if sender.is_staff is False and sender.id != ticket.created_by.id:
            raise PermissionDenied

        if ticket.status == RestaurantTicket.CLOSED:
            raise ValidationError(
                {"non_field_errors": ["This ticket has been closed."]}
            )

        message = RestaurantMessage.objects.create(**validated_data)
        send_message_notification.delay(message.id)
        return message
