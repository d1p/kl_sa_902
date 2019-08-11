from django.conf import settings
from django.core.validators import EmailValidator
from django.utils import timezone
from rest_framework import serializers
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from six import text_type

from apps.account.models import User
from .models import _PHONE_REGEX


class UserSerializer(serializers.ModelSerializer):
    password = serializers.CharField(
        style={"input_type": "password"}, write_only=True, required=False, min_length=8
    )

    @property
    def _user(self):
        return self.context["request"].user

    def validate_email(self, value):
        try:
            if value == self._user.email:
                return value
            else:
                if User.objects.filter(email=value).exists():
                    raise serializers.ValidationError(
                        {"email": "Email address is already registered"}
                    )
                return value
        except AttributeError:
            return value

    def validate_phone_number(self, value):
        try:
            if value == self._user.phone_number:
                return value
            else:
                if User.objects.filter(phone_number=value).exists():
                    raise serializers.ValidationError(
                        {"email": "Phone Number is already registered"}
                    )
                return value
        except AttributeError:
            return value

    class Meta:
        model = User
        fields = (
            "id",
            "name",
            "phone_number",
            "email",
            "password",
            "profile_picture",
            "phone_number_verified",
            "locale",
        )
        read_only_fields = ("id", "phone_number_verified", "created_at")
        extra_kwargs = {
            "email": {"validators": [EmailValidator()]},
            "phone_number": {"validators": [_PHONE_REGEX]},
        }


class MyTokenObtainPairSerializer(TokenObtainPairSerializer):
    def validate(self, attrs):
        data = super(TokenObtainPairSerializer, self).validate(attrs)
        refresh = self.get_token(self.user)
        data["refresh"] = text_type(refresh)
        data["access"] = text_type(refresh.access_token)
        data["access_token_lifetime"] = settings.SIMPLE_JWT[
            "ACCESS_TOKEN_LIFETIME"
        ].total_seconds()
        data["refresh_token_lifetime"] = settings.SIMPLE_JWT[
            "REFRESH_TOKEN_LIFETIME"
        ].total_seconds()
        data["user"] = (
            {
                "id": self.user.id,
                "phone_number": self.user.phone_number,
                "profile_picture": self.user.profile_picture.url,
                "email": self.user.email,
                "name": self.user.name,
            },
        )
        data["profile_type"] = self.user.profile_type
        self.user.last_login = timezone.now()
        self.user.save()
        return data


class ForgotPasswordSerializer(serializers.Serializer):
    phone_number = serializers.CharField(required=True)


class ResetPasswordSerializer(serializers.Serializer):
    phone_number = serializers.CharField(required=True)
    code = serializers.IntegerField(required=True)
    new_password = serializers.CharField(required=True, min_length=8)


class ChangePasswordSerializer(serializers.Serializer):
    current_password = serializers.CharField(required=True)
    new_password = serializers.CharField(required=True, min_length=8)


class ResendVerificationSerializer(serializers.Serializer):
    phone_number = serializers.CharField(required=True)


class VerifyPhoneNumberSerializer(serializers.Serializer):
    phone_number = serializers.CharField(required=True)
    code = serializers.CharField(required=True)

