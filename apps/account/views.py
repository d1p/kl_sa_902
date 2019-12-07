from django.db import transaction
from django.utils import timezone
from rest_framework import permissions, status
from rest_framework.mixins import CreateModelMixin
from rest_framework.response import Response
from rest_framework.viewsets import GenericViewSet
from twilio.base.exceptions import TwilioRestException

from apps.account.models import (
    User,
    ForgotPasswordToken,
    VerifyPhoneToken,
    ChangePhoneNumberToken,
)
from rest_framework_simplejwt.views import TokenObtainPairView
from .serializers import (
    MyTokenObtainPairSerializer,
    ChangePasswordSerializer,
    ForgotPasswordSerializer,
    ResetPasswordSerializer,
    ResendVerificationSerializer,
    VerifyPhoneNumberSerializer,
    ChangePhoneNumberVerificationSerializer,
    ChangePhoneNumberSerializer,
    ResetTokenCheckSerializer,
)
from .tasks import send_password_change_alert


# Create your views here.
class MyTokenObtainPairView(TokenObtainPairView):
    serializer_class = MyTokenObtainPairSerializer


class ChangePasswordViewSet(GenericViewSet, CreateModelMixin):
    """
    On success
    ```json {
        "success": true
    }```

    upon successfully changing the password, else returns the errors
    """

    serializer_class = ChangePasswordSerializer
    permission_classes = [permissions.IsAuthenticated]
    queryset = None

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid() is False:
            return Response(data=serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        user = request.user
        if (
            user.check_password(serializer.validated_data.get("current_password"))
            is False
        ):
            return Response(
                {"current_password": ["Incorrect password"]},
                status=status.HTTP_400_BAD_REQUEST,
            )

        user.set_password(serializer.validated_data.get("new_password"))
        user.save()
        return Response({"success": True}, status=status.HTTP_200_OK)


class ForgotPasswordViewSet(GenericViewSet, CreateModelMixin):
    serializer_class = ForgotPasswordSerializer
    permission_classes = [permissions.AllowAny]

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid() is False:
            return Response(data=serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        try:
            user = User.objects.get(
                phone_number=serializer.validated_data.get("phone_number")
            )
        except User.DoesNotExist:
            return Response(
                {"phone_number": ["User does not exists."]}, status.HTTP_400_BAD_REQUEST
            )

        if ForgotPasswordToken.has_sent_recently(user) is True:
            return Response(
                {"non_field_errors": "Please wait before requesting for a new code."},
                status=status.HTTP_429_TOO_MANY_REQUESTS,
            )

        token = ForgotPasswordToken.objects.create(user=user)
        user.sms_user(f"Use {token.code} as your reset code for Kole.")

        return Response({"success": True}, status=status.HTTP_200_OK)


class ResetPasswordViewSet(GenericViewSet, CreateModelMixin):
    permission_classes = [permissions.AllowAny]
    serializer_class = ResetPasswordSerializer

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid() is False:
            return Response(data=serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        try:
            user = User.objects.get(
                phone_number=serializer.validated_data.get("phone_number")
            )
        except User.DoesNotExist:
            raise Response(
                {"phone_number": ["Invalid phone number."]},
                status=status.HTTP_400_BAD_REQUEST,
            )

        if ForgotPasswordToken.objects.filter(
            user=user, code=serializer.validated_data.get("code")
        ).exists():
            user.set_password(serializer.validated_data.get("new_password"))
            user.save()
            ForgotPasswordToken.objects.filter(
                user=user, created_at__lte=timezone.now()
            ).delete()

            # send password changed alert.
            send_password_change_alert.delay(user_id=user.id)

            return Response({"success": True}, status=status.HTTP_200_OK)
        else:
            return Response(
                {"code": ["Invalid code."]}, status=status.HTTP_400_BAD_REQUEST
            )


class ResendVerificationViewSet(GenericViewSet, CreateModelMixin):
    serializer_class = ResendVerificationSerializer
    permission_classes = [permissions.AllowAny]

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid() is False:
            return Response(data=serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        try:
            user = User.objects.get(
                phone_number=serializer.validated_data.get("phone_number")
            )
        except User.DoesNotExist:
            return Response(status=status.HTTP_404_NOT_FOUND)

        if VerifyPhoneToken.has_sent_recently(user) is True:
            return Response(
                {"non_field_errors": "Please wait before requesting for a new code."},
                status=status.HTTP_429_TOO_MANY_REQUESTS,
            )

        token = VerifyPhoneToken.objects.create(user=user)

        user.sms_user(f"Use {token.code} as your verification code for Kole.")
        return Response({"success": True}, status=status.HTTP_200_OK)


class VerifyPhoneNumberViewSet(GenericViewSet, CreateModelMixin):
    serializer_class = VerifyPhoneNumberSerializer
    permission_classes = [permissions.AllowAny]

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid() is False:
            return Response(data=serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        try:
            user = User.objects.get(
                phone_number=serializer.validated_data.get("phone_number")
            )
        except User.DoesNotExist:
            return Response(
                {"phone_number": ["Invalid phone number."]},
                status=status.HTTP_400_BAD_REQUEST,
            )

        if user.is_active is True:
            return Response(
                {"non_field_error": "Account is already verified."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        if VerifyPhoneToken.objects.filter(
            user=user, code=serializer.validated_data.get("code")
        ).exists():
            user.is_active = True
            user.phone_number_verified = True
            user.save()
            VerifyPhoneToken.objects.filter(user=user).delete()
            return Response({"success": True}, status=status.HTTP_200_OK)
        else:
            return Response(status=status.HTTP_404_NOT_FOUND)


class ChangePhoneNumberViewSet(GenericViewSet, CreateModelMixin):
    """
    Responses other than the default validation ones are given bellow
    ```{"success": true}```
    ```{"password": ["Invalid Password"]}```
    ```{"new_phone_number": ["Phone Number is already registered"]}```
    ```{"new_phone_number": ["Invalid phone Number."]}```
    """

    serializer_class = ChangePhoneNumberSerializer

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid() is False:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        if (
            request.user.check_password(serializer.validated_data.get("password"))
            is False
        ):
            return Response(
                {"password": ["Invalid Password."]}, status=status.HTTP_400_BAD_REQUEST
            )

        if User.objects.filter(
            phone_number=serializer.validated_data.get("new_phone_number")
        ).exists():
            return Response(
                {"new_phone_number": ["Phone Number is already registered"]},
                status=status.HTTP_400_BAD_REQUEST,
            )

        with transaction.atomic():
            token = ChangePhoneNumberToken.objects.create(
                user=request.user,
                old_phone_number=request.user.phone_number,
                new_phone_number=serializer.validated_data.get("new_phone_number"),
            )
            try:
                request.user.sms_user(
                    f"Use {token.code} as verification code for Kole."
                )
            except TwilioRestException:
                return Response(
                    {"new_phone_number": ["Invalid phone Number."]},
                    status=status.HTTP_400_BAD_REQUEST,
                )

            return Response({"success": True}, status=status.HTTP_200_OK)


class ChangePhoneNumberVerificationViewSet(GenericViewSet, CreateModelMixin):
    """
    Responses other than the default validation ones are given bellow
    ```{"success": true}```
    ```{"code": "Invalid Code"}```
    """

    serializer_class = ChangePhoneNumberVerificationSerializer

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid() is False:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        if ChangePhoneNumberToken.objects.filter(
            user=request.user,
            old_phone_number=request.user.phone_number,
            new_phone_number=serializer.validated_data.get("new_phone_number"),
            code=serializer.validated_data.get("code"),
        ).exists():
            request.user.phone_number = serializer.validated_data.get(
                "new_phone_number"
            )
            request.user.save()
            ChangePhoneNumberToken.objects.filter(
                user=request.user,
                old_phone_number=request.user.phone_number,
                new_phone_number=serializer.validated_data.get("new_phone_number"),
                code=serializer.validated_data.get("code"),
            ).delete()
            return Response({"success": True}, status=status.HTTP_200_OK)
        else:
            return Response({"code": "Invalid Code"}, status.HTTP_400_BAD_REQUEST)


class CheckResetTokenViewSet(GenericViewSet, CreateModelMixin):
    """
    returns {"valid": true} for valid code and {"valid": false } for invalid code.
    Note: This only checks if there is a code sent from the reset password api. Not the time restriction of it.
    """

    permission_classes = [permissions.AllowAny]
    serializer_class = ResetTokenCheckSerializer

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid() is False:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        return Response(
            {
                "valid": ForgotPasswordToken.objects.filter(
                    user__phone_number=serializer.validated_data.get("phone_number"),
                    code=serializer.validated_data.get("code"),
                ).exists()
            },
            status=status.HTTP_200_OK,
        )

