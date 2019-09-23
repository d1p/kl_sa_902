from django.contrib import admin

from .models import Ticket, ReportIssue


@admin.register(Ticket)
class TicketAdmin(admin.ModelAdmin):
    list_display = ("id", "created_by", "topic", "created_at", "last_updated", "status")
    list_filter = ("status", "created_by__groups")

    search_fields = ("created_by__name",)


@admin.register(ReportIssue)
class ReportIssueAdmin(admin.ModelAdmin):
    list_display = ("id", "created_by", "topic", "order", "created_at", "status")
    list_filter = ("status",)
    search_fields = ("created_by__name", "order__id")
