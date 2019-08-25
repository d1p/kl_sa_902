from django.contrib import admin

from apps.account.models import User
from .models import Category, Restaurant, RestaurantTable


class OnlyRestaurantInUserAdmin(admin.ModelAdmin):
    def get_form(self, request, obj=None, **kwargs):
        form = super(OnlyRestaurantInUserAdmin, self).get_form(request, obj, **kwargs)
        if obj is None:
            form.base_fields["user"].queryset = User.objects.filter(
                groups__name="Restaurant", restaurant__is_public=True
            )
        else:
            form.base_fields["user"].queryset = User.objects.filter(id=obj.user.id)
        form.base_fields["user"].widget.can_add_related = False
        return form


class RestaurantInline(admin.StackedInline):
    def __init__(self, *args, **kwargs):
        super(RestaurantInline, self).__init__(*args, **kwargs)
        self.can_delete = False

    model = Restaurant


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ("id", "name", "name_in_ar")
    search_fields = ("name", "name_in_ar")
    date_hierarchy = "created_at"


@admin.register(Restaurant)
class RestaurantAdmin(admin.ModelAdmin):
    list_display = ("name", "email_address", "phone_number", "is_public")
    search_fields = ("user__name", "user__email_address", "user__phone_number")
    list_filter = ("is_public",)

    def name(self, obj):
        return obj.user.name

    def email_address(self, obj):
        return obj.user.email

    def phone_number(self, obj):
        return obj.user.phone_number


@admin.register(RestaurantTable)
class RestaurantTableAdmin(OnlyRestaurantInUserAdmin):
    list_display = ("id", "name", "user", "is_active")
    list_filter = ("is_active",)
    search_fields = ("user__name", "user__phone_number")
    date_hierarchy = "created_at"
