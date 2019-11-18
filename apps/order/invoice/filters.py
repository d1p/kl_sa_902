from django_filters import rest_framework as filters

from apps.order.invoice.models import Invoice


class InvoiceFilter(filters.FilterSet):
    created_at = filters.DateTimeFromToRangeFilter(field_name="created_at")

    class Meta:
        model = Invoice
        fields = ["created_at"]
