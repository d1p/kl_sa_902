from django_filters import rest_framework as filters

from apps.order.invoice.models import Invoice


class InvoiceFilter(filters.FilterSet):
    class Meta:
        model = Invoice
        fields = {"created_at": ["range"]}
