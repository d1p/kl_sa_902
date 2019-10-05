from rest_framework.viewsets import GenericViewSet
from rest_framework import mixins

from apps.account.types import ProfileType
from .serializers import InvoiceSerializer
from .models import Invoice, InvoiceItem


class InvoiceViewSet(GenericViewSet, mixins.CreateModelMixin):
    serializer_class = InvoiceSerializer

    def get_queryset(self):
        user = self.request.user
        if user.profile_type == ProfileType.CUSTOMER:
            queryset = Invoice.objects.filter(order__order_participants__user=user)
        elif user.profile_type == ProfileType.RESTAURANT:
            queryset = Invoice.objects.filter(order__restaurant=user)
        else:
            queryset = Invoice.objects.all()

        return queryset
