from django_filters import rest_framework as filters

from .models import RestaurantTable, Restaurant


class RestaurantFilter(filters.FilterSet):
    name = filters.CharFilter(lookup_expr="icontains", field_name="user__name")

    class Meta:
        model = Restaurant
        fields = ("name",)


class RestaurantTableFilter(filters.FilterSet):
    user = filters.NumberFilter(lookup_expr="exact", field_name="user__id")

    class Meta:
        model = RestaurantTable
        fields = ("user",)
