from django.contrib import admin

from .models import Category, Restaurant


class RestaurantInline(admin.StackedInline):
    def __init__(self, *args, **kwargs):
        super(RestaurantInline, self).__init__(*args, **kwargs)
        self.can_delete = False

    model = Restaurant


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ("id", "name", "name_in_ar", )
    search_fields = ("name", "name_in_ar")
    date_hierarchy = "created_at"


@admin.register(Restaurant)
class RestaurantAdmin(admin.ModelAdmin):
    list_display = ("name", "email_address", "phone_number", "is_public")
    search_fields = ("user__name", "user__email_address", "user__phone_number")
    list_filter = ("is_public", )

    def name(self, obj):
        return obj.user.name

    def email_address(self, obj):
        return obj.user.email

    def phone_number(self, obj):
        return obj.user.phone_number
