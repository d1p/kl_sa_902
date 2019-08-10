from django.utils.translation import ugettext_lazy as _
from rest_framework import permissions, status
from rest_framework.mixins import CreateModelMixin
from rest_framework.response import Response
from rest_framework.viewsets import GenericViewSet
from rest_framework_simplejwt.views import TokenObtainPairView

from .serializers import MyTokenObtainPairSerializer, ChangePasswordSerializer


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
        if user.check_password(serializer.validated_data.get("current_password")) is False:
            return Response({"current_password": ["Incorrect password"]}, status=status.HTTP_400_BAD_REQUEST)

        user.set_password(serializer.validated_data.get("new_password"))
        user.save()
        return Response({"success": True}, status=status.HTTP_200_OK)
