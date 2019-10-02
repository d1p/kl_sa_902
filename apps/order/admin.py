from django.contrib import admin

from .models import (
    Order,
    OrderInvite,
    OrderParticipant,
    OrderItem,
    OrderItemAddOn,
    OrderItemAttributeMatrix,
    OrderItemInvite,
)

admin.site.register(Order)

admin.register(OrderItemAddOn)


class OrderItemAddOnInline(admin.TabularInline):
    model = OrderItemAddOn
    readonly_fields = ("food_add_on", "quantity",)
    extra = 0

    def has_add_permission(self, request, obj=None):
        return False

    def has_delete_permission(self, request, obj=None):
        return False

    def has_change_permission(self, request, obj=None):
        return False

class OrderItemMatrixInline(admin.TabularInline):
    model = OrderItemAttributeMatrix
    readonly_fields = ("food_attribute_matrix",)
    extra = 0

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
    list_display = ("id", "order", "quantity", "total_price",)
    list_display_links = ("id", "order",)
    inlines = [OrderItemAddOnInline, OrderItemMatrixInline]

    def has_add_permission(self, request):
        return False

    def has_change_permission(self, request, obj=None):
        return False


admin.site.register(OrderItemAttributeMatrix)
admin.site.register(OrderItemInvite)
