from django.conf import settings
from django.core.validators import EmailValidator
from django.utils import timezone
from rest_framework import serializers
from six import text_type

from apps.account.models import User
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from .models import _PHONE_REGEX
from .types import ProfileType


class PublicUserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ("id", "name", "profile_picture")
        read_only_fields = ("id", "name", "profile_picture")


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
            "phone_number": {"validators": [_PHONE_REGEX], "required": False},
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
        data["user"] = [
            {
                "id": self.user.id,
                "phone_number": self.user.phone_number,
                "email": self.user.email,
                "name": self.user.name,
            }
        ]
        try:
            data["user"][0]["profile_picture"] = self.user.profile_picture.url
        except ValueError:
            data["user"][0]["profile_picture"] = None

        data["profile_type"] = self.user.profile_type
        if self.user.profile_type == ProfileType.CUSTOMER:
            try:
                data["customer"] = {"qr_code": self.user.customer.qr_code.url}
            except ValueError:
                pass
        elif self.user.profile_type == ProfileType.RESTAURANT:
            data["restaurant"] = {"is_public": self.user.restaurant.is_public}

        self.user.last_login = timezone.now()
        self.user.save()
        return data


class ForgotPasswordSerializer(serializers.Serializer):
    phone_number = serializers.CharField(required=True)


class ResetPasswordSerializer(serializers.Serializer):
    phone_number = serializers.CharField(required=True)
    code = serializers.IntegerField(required=True)
    new_password = serializers.CharField(required=True, min_length=8)


class ResetTokenCheckSerializer(serializers.Serializer):
    phone_number = serializers.CharField(required=True)
    code = serializers.IntegerField(required=True)


class ChangePasswordSerializer(serializers.Serializer):
    current_password = serializers.CharField(required=True)
    new_password = serializers.CharField(required=True, min_length=8)


class ResendVerificationSerializer(serializers.Serializer):
    phone_number = serializers.CharField(required=True)


class VerifyPhoneNumberSerializer(serializers.Serializer):
    phone_number = serializers.CharField(required=True)
    code = serializers.CharField(required=True)


class ChangePhoneNumberSerializer(serializers.Serializer):
    password = serializers.CharField(required=True)
    new_phone_number = serializers.CharField(
        required=True, validators=[_PHONE_REGEX], max_length=17
    )


class ChangePhoneNumberVerificationSerializer(serializers.Serializer):
    new_phone_number = serializers.CharField(
        required=True, validators=[_PHONE_REGEX], max_length=17
    )
    code = serializers.CharField(required=True)
