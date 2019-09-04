from django_filters import rest_framework as filters

from .models import FoodAddOn, FoodItem, FoodAttribute


class FoodItemFilter(filters.FilterSet):
    name = filters.CharFilter(lookup_expr="icontains", field_name="name")
    category = filters.NumberFilter(lookup_expr="exact", field_name="category__id")
    user = filters.NumberFilter(lookup_expr="exact", field_name="user__id")

    class Meta:
        model = FoodItem
        fields = ("name", "category", "user")


class FoodAddOnFilter(filters.FilterSet):
    food = filters.NumberFilter(lookup_expr="exact", field_name="food__id")

    class Meta:
        model = FoodAddOn
        fields = ("food",)


class FoodAttributeFilter(filters.FilterSet):
    food = filters.NumberFilter(lookup_expr="exact", field_name="food__id")

    class Meta:
        model = FoodAttribute
        fields = ("food",)
