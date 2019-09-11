from django_filters import rest_framework as filters
from .models import Order, OrderItem


class OrderFilter(filters.FilterSet):
    class Meta:
        model = Order
        fields = {
            "id": ["exact"],
            "order_type": ["exact"],
            "restaurant": ["exact"],
            "table": ["exact"],
            "status": ["exact"],
            "created_by": ["exact"],
            "created_at": ["range"],
        }


class OrderItemFilter(filters.FilterSet):
    class Meta:
        model = OrderItem
        fields = {
            "food_item": ["exact"],
            "quantity": ["exact"],
            "order": ["exact"],
            "status": ["exact"],
            "added_by": ["exact"],
        }
