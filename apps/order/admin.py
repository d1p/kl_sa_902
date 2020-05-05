from django.contrib import admin
from django.utils.safestring import mark_safe
from django.utils.translation import gettext_lazy

from .models import (
    Order,
    OrderInvite,
    OrderParticipant,
    OrderItem,
    OrderItemAddOn,
    OrderItemAttributeMatrix,
    OrderItemInvite,
    Rating,
)
from .types import OrderStatusType


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "status",
        "order_type",
        "restaurant",
        "created_by",
        "confirmed",
        "invoice_link",
        "table",
        "created_at",
    )
    list_filter = ("status", "order_type", "confirmed", "has_restaurant_accepted",)
    search_fields = ("id",)

    def invoice_link(self, obj: Order):
        if obj.status is OrderStatusType.COMPLETED:
            return mark_safe(
                f"<a href='/invoice/view/{obj.id}/' target='_blank'>View Invoice</a>"
            )
        else:
            return gettext_lazy("Order hasn't been completed yet.")

    invoice_link.short_description = ""


admin.register(OrderItemAddOn)


class OrderItemAddOnInline(admin.TabularInline):
    model = OrderItemAddOn
    readonly_fields = ("food_add_on", "quantity")
    extra = 0

    def has_add_permission(self, request, obj=None):
        return False

    def has_delete_permission(self, request, obj=None):
        return False

    def has_change_permission(self, request, obj=None):
        return False


class OrderItemMatrixInline(admin.TabularInline):
    model = OrderItemAttributeMatrix
    readonly_fields = ("name", "food_attribute_matrix")
    extra = 0

    def name(self, obj):
        return obj.food_attribute_matrix.attribute.name

    def has_add_permission(self, request, obj=None):
        return False

    def has_delete_permission(self, request, obj=None):
        return False

    def has_change_permission(self, request, obj=None):
        return False


@admin.register(OrderInvite)
class OrderInviteAdmin(admin.ModelAdmin):
    list_display = ("id", "invited_user", "invited_by", "order", "status", "created_at")
    list_display_links = ("invited_user", "invited_by", "order")


@admin.register(OrderParticipant)
class OrderParticipantAdmin(admin.ModelAdmin):
    list_display = ("id", "user", "order", "created_at")


@admin.register(OrderItem)
class OrderItemAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "order",
        "quantity",
        "total_price_without_tax",
        "total_price_with_tax",
        "total_tax",
        "shared_price_without_tax",
        "shared_price_with_tax",
        "shared_total_tax",
    )
    list_display_links = ("id", "order")
    inlines = [OrderItemAddOnInline, OrderItemMatrixInline]

    def has_add_permission(self, request):
        return False

    def has_change_permission(self, request, obj=None):
        return False


admin.site.register(OrderItemAttributeMatrix)
admin.site.register(OrderItemInvite)

admin.site.register(Rating)
