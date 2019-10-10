from rest_framework import mixins
from rest_framework.viewsets import GenericViewSet, ReadOnlyModelViewSet

from utils.permission import IsAuthenticatedOrCreateOnly
from .models import Customer, Misc
from .serializers import CustomerSerializer, MiscSerializer


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


class MiscViewSet(ReadOnlyModelViewSet):
    lookup_field = "user"

    def get_queryset(self):
        return Misc.objects.filter(user=self.request.user)

    serializer_class = MiscSerializer
