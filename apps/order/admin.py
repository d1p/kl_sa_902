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


@admin.register(OrderInvite)
class OrderInviteAdmin(admin.ModelAdmin):
    list_display = ("id", "invited_user", "invited_by", "order", "status", "created_at")
    list_display_links = ("invited_user", "invited_by", "order")


@admin.register(OrderParticipant)
class OrderParticipantAdmin(admin.ModelAdmin):
    list_display = ("id", "user", "order", "created_at")


admin.site.register(OrderItem)
admin.site.register(OrderItemAddOn)
admin.site.register(OrderItemAttributeMatrix)
admin.site.register(OrderItemInvite)
