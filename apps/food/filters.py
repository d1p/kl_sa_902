from django_filters import rest_framework as filters

from .models import FoodAddOn, FoodItem, FoodAttribute


class FoodItemFilter(filters.FilterSet):
    class Meta:
        model = FoodItem
        fields = {"name": ["icontains"], "category": ["exact"], "user": ["exact"]}


class FoodAddOnFilter(filters.FilterSet):
    class Meta:
        model = FoodAddOn
        fields = {"food": ["exact"]}


class FoodAttributeFilter(filters.FilterSet):
    class Meta:
        model = FoodAttribute
        fields = {"food": ["exact"]}
