from django.contrib import admin
from django.utils import translation

from .models import (
    RestaurantTicket,
    ReportIssue,
    PreBackedTicketTopic,
    CustomerTicketTopic,
    CustomerTicket,
)

admin.site.register(PreBackedTicketTopic)
admin.site.register(CustomerTicketTopic)


@admin.register(CustomerTicket)
class RestaurantTicketAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "created_by",
        "topic",
        "sub_topic",
        "created_at",
        "last_updated",
        "status",
    )

    generic_list_filter = ("status", )

    search_fields = ("created_by__name",)

    def get_list_filter(self, request):
        current_language = translation.get_language()
        if current_language == "ar":
            return self.generic_list_filter + ("topic__text_in_ar",)
        else:
            return self.generic_list_filter + ("topic__text",)


@admin.register(RestaurantTicket)
class RestaurantTicketAdmin(admin.ModelAdmin):
    list_display = ("id", "created_by", "topic", "created_at", "last_updated", "status")
    list_filter = ("status",)

    search_fields = ("created_by__name",)


@admin.register(ReportIssue)
class ReportIssueAdmin(admin.ModelAdmin):
    list_display = ("id", "created_by", "topic", "order", "created_at", "status")
    list_filter = ("status",)
    search_fields = ("created_by__name", "order__id")
