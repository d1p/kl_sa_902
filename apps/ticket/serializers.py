from rest_framework import serializers

from apps.account.serializers import UserSerializer
from .models import Ticket


class TicketSerializer(serializers.ModelSerializer):
    created_by = UserSerializer(required=False)

    class Meta:
        model = Ticket
        fields = ("id", "created_by", "topic", "description", )
        read_only_fields = ("id", "created_at", "created_by", )
