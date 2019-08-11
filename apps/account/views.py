from django.utils import timezone
from rest_framework import permissions, status
from rest_framework.mixins import CreateModelMixin
from rest_framework.response import Response
from rest_framework.viewsets import GenericViewSet
from rest_framework_simplejwt.views import TokenObtainPairView

from apps.account.models import User, ForgotPasswordToken
from .serializers import (
    MyTokenObtainPairSerializer,
    ChangePasswordSerializer,
    ForgotPasswordSerializer,
    ResetPasswordSerializer,
)


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
            return Response({"success": True}, status=status.HTTP_200_OK)
        else:
            return Response(
                {"code": ["Invalid code."]}, status=status.HTTP_400_BAD_REQUEST
            )
