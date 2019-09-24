from django.contrib import admin

from .models import RestaurantTicket, ReportIssue


@admin.register(RestaurantTicket)
class RestaurantTicketAdmin(admin.ModelAdmin):
    list_display = ("id", "created_by", "topic", "created_at", "last_updated", "status")
    list_filter = ("status", )

    search_fields = ("created_by__name",)


@admin.register(ReportIssue)
class ReportIssueAdmin(admin.ModelAdmin):
    list_display = ("id", "created_by", "topic", "order", "created_at", "status")
    list_filter = ("status",)
    search_fields = ("created_by__name", "order__id")
