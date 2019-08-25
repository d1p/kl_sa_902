from django.contrib import admin
from nested_admin.nested import NestedModelAdmin, NestedTabularInline

from apps.account.restaurant.admin import OnlyRestaurantInUserAdmin
from .models import (
    FoodCategory,
    FoodItem,
    FoodAddOn,
    FoodAttribute,
    FoodAttributeMatrix,
)

admin.site.register(FoodAttribute)
admin.site.register(FoodAttributeMatrix)


@admin.register(FoodCategory)
class FoodCategoryAdmin(OnlyRestaurantInUserAdmin):
    list_display = ("id", "name", "user", "is_active", "created_at")
    list_filter = ("is_active",)
    search_fields = ("user__name",)
    date_hierarchy = "created_at"


class FoodAddOnInline(NestedTabularInline):
    model = FoodAddOn
    classes = "collapse"
    fields = ("name", "price")
    sortable_field_name = "name"


class FoodAttributeMatrixInline(NestedTabularInline):
    model = FoodAttributeMatrix
    sortable_field_name = "name"
    extra = 2



class FoodAttributeInline(NestedTabularInline):
    model = FoodAttribute
    inlines = [FoodAttributeMatrixInline]
    sortable_field_name = "name"
    extra = 1


class FoodItemAdmin(NestedModelAdmin, OnlyRestaurantInUserAdmin):
    list_display = (
        "id",
        "name",
        "user",
        "category",
        "price",
        "is_active",
        "created_at",
    )
    list_filter = ("category", "created_at", "price")
    search_fields = ("user", "name")
    date_hierarchy = "created_at"
    inlines = [FoodAddOnInline, FoodAttributeInline]


admin.site.register(FoodItem, FoodItemAdmin)
