from rest_framework import mixins
from rest_framework.viewsets import GenericViewSet

from utils.permission import IsAuthenticatedOrCreateOnly
from .models import Customer
from .serializers import CustomerSerializer


class CustomerViewSet(
    GenericViewSet,
    mixins.CreateModelMixin,
    mixins.UpdateModelMixin,
    mixins.RetrieveModelMixin,
):
    permission_classes = [IsAuthenticatedOrCreateOnly]
    queryset = Customer.objects.all()
    lookup_field = "user"
    serializer_class = CustomerSerializer
