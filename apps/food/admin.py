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
    list_display = ("id", "name", "user", "is_deleted", "created_at")
    list_filter = ("is_deleted",)
    search_fields = ("user__name",)
    date_hierarchy = "created_at"


class FoodAddOnInline(NestedTabularInline):
    model = FoodAddOn
    sortable_field_name = None


class FoodAttributeMatrixInline(NestedTabularInline):
    model = FoodAttributeMatrix
    sortable_field_name = None
    extra = 2


class FoodAttributeInline(NestedTabularInline):
    model = FoodAttribute
    inlines = [FoodAttributeMatrixInline]
    sortable_field_name = None

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
    search_fields = ("user__id", "name")
    date_hierarchy = "created_at"
    inlines = [FoodAttributeInline, FoodAddOnInline]


admin.site.register(FoodItem, FoodItemAdmin)
