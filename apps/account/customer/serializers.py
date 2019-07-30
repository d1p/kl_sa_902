from django.contrib.auth.models import Group
from django.db import IntegrityError, transaction
from rest_framework import serializers
from rest_framework.exceptions import PermissionDenied, ValidationError
from django.utils.translation import ugettext_lazy as _
from apps.account.models import User
from apps.account.customer.models import Customer
from apps.account.serializers import UserSerializer


class CustomerSerializer(serializers.ModelSerializer):
    user = UserSerializer(required=True)

    class Meta:
        model = Customer
        fields = ("user",)

    def create(self, validated_data):
        group = Group.objects.get(name="Customer")
        user_data = validated_data.pop("user")

        if user_data.get("password") is None:
            raise ValidationError(
                {"user": {"password": ["This field may not be blank."]}}
            )

        with transaction.atomic():
            try:
                user = User.objects.create(
                    full_name=user_data.get("full_name"),
                    phone_number=user_data.get("phone_number"),
                    email=user_data.get("email"),
                    locale=user_data.get("locale"),
                    profile_picture=user_data.get("profile_picture"),
                )
            except IntegrityError:
                raise ValidationError(
                    {"user": {"email": ["Email address is already registered"]}}
                )

            user.set_password(user_data.get("password"))

            user.groups.add(group)
            user.save()

            customer = Customer.objects.create(user=user)

            return customer

    def update(self, instance, validated_data):
        user_data = validated_data.pop("user", {})

        with transaction.atomic():
            instance.user.full_name = user_data.get(
                "full_name", instance.user.full_name
            )
            try:
                instance.user.email = user_data.get("email", instance.user.email)
            except IntegrityError:
                raise ValidationError(
                    {"user": {"email": [_("Email address is already registered")]}}
                )
            instance.user.locale = user_data.get("locale", instance.user.locale)
            instance.user.profile_picture = user_data.get(
                "profile_picture", instance.user.profile_picture
            )
            instance.save()
            return instance
