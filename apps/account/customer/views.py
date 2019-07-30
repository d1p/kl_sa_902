from rest_framework.viewsets import GenericViewSet
from rest_framework.permissions import AllowAny
from rest_framework import mixins, status
from rest_framework.response import Response

from utils.permission import IsAuthenticatedOrCreateOnly
from .serializers import CustomerSerializer
from .models import Customer


class CustomerViewSet(
    GenericViewSet,
    mixins.CreateModelMixin,
    mixins.UpdateModelMixin,
    mixins.RetrieveModelMixin,
):
    permission_classes = [IsAuthenticatedOrCreateOnly]
    queryset = Customer.objects.all()
    lookup_field = "user"

    def get_serializer_class(self):
        return CustomerSerializer

    def perform_create(self, serializer):
        serializer.save()

    def perform_update(self, serializer):
        instance = self.get_object()
        if instance.user != self.request.user:
            return Response(status.HTTP_401_UNAUTHORIZED)
        serializer.save()
