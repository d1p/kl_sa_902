from django.conf import settings
from rest_framework import serializers
from rest_framework.exceptions import ValidationError
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from six import text_type

from apps.account.models import User, PhoneVerification


class UserSerializer(serializers.ModelSerializer):
    password = serializers.CharField(
        style={"input_type": "password"}, write_only=True, required=False, min_length=8
    )

    class Meta:
        model = User
        fields = (
            "id",
            "full_name",
            "phone_number",
            "email",
            "password",
            "profile_picture",
            "phone_number_verified",
            "locale",
        )
        read_only_fields = ("id", "phone_number_verified")


class MyTokenObtainPairSerializer(TokenObtainPairSerializer):
    def validate(self, attrs):
        data = super(TokenObtainPairSerializer, self).validate(attrs)
        if self.user.email_verified is False:
            raise ValidationError({"email": ["Email is not verified yet."]})

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
            },
        )
        data["profile_type"] = self.user.profile_type

        return data


class ForgotPasswordSerializer(serializers.Serializer):
    phone_number = serializers.CharField(required=True)

    def create(self, validated_data):
        try:
            user = User.objects.get(phone_number=validated_data.get("phone_number"))
        except User.DoesNotExist:
            raise ValidationError({"phone_number": ["User does not exists."]})
        if PhoneVerification.has_sent_recently(user) is True:
            raise ValidationError({"non_field_errors": "Please wait before requesting for a new code."})
        
        return PhoneVerification.objects.create(user=user)


class ResetPasswordSerializer(serializers.Serializer):
    phone_number = serializers.CharField(required=True)
    code = serializers.IntegerField(required=True)
    new_password = serializers.CharField(required=True)


class ChangePasswordSerializer(serializers.Serializer):
    current_password = serializers.CharField(required=True)
    new_password = serializers.CharField(required=True)
