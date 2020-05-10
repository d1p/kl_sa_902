from django_filters import rest_framework as filters

from apps.order.invoice.models import Invoice


class InvoiceFilter(filters.FilterSet):
    created_at = filters.DateTimeFromToRangeFilter(field_name="created_at")
    order_type = filters.NumberFilter(lookup_expr="exact", field_name="order__order_type")

    class Meta:
        model = Invoice
        fields = ["created_at", "order_type", ]
