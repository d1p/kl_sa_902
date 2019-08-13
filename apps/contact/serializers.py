from django.db import IntegrityError
from rest_framework import serializers
from rest_framework.exceptions import ValidationError

from apps.account.models import User
from .models import ContactGroup


class ContactUserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ("id", "name", "phone_number", "profile_picture")
        read_only_fields = ("id", "name", "phone_number", "profile_picture")


class ContactListSyncSerializer(serializers.Serializer):
    contacts = serializers.ListField(child=serializers.CharField())


class ContactGroupSerializer(serializers.ModelSerializer):
    contacts = ContactUserSerializer(many=True, read_only=True)

    class Meta:
        model = ContactGroup
        fields = ("id", "name", "contacts", "created_at")
        read_only_fields = ("id", "created_at")

    def create(self, validated_data):
        try:
            return ContactGroup.objects.create(**validated_data)
        except IntegrityError:
            raise ValidationError({"name": "Name already exists."})

class IdSerializer(serializers.Serializer):
    id = serializers.IntegerField(required=True)
