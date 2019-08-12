from django.contrib import admin
from .models import Ticket, Message


@admin.register(Ticket)
class TicketAdmin(admin.ModelAdmin):
    list_display = ("id", "created_by", "topic", "created_at", "last_updated", "status",)
    list_filter = ("status", )
    search_fields = ("created_by__name", )

