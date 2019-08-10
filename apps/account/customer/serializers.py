from django.db import transaction
from rest_framework import serializers
from rest_framework.exceptions import PermissionDenied

from apps.account.customer.models import Customer
from apps.account.serializers import UserSerializer
from ..utils import register_basic_user, save_user_information


class CustomerSerializer(serializers.ModelSerializer):
    user = UserSerializer(required=True)

    class Meta:
        model = Customer
        fields = ("qr_code", "user")
        read_only_fields = ("qr_code",)

    def create(self, validated_data):
        user_data = validated_data.pop("user")

        with transaction.atomic():
            user = register_basic_user("Customer", user_data)
            customer = Customer.objects.create(user=user)
            return customer

    def update(self, instance, validated_data):
        request_user = self.context["request"].user

        if request_user != instance.user:
            raise PermissionDenied

        user_data = validated_data.pop("user", {})

        with transaction.atomic():
            save_user_information(instance.user, user_data)
        return instance
