from django.contrib import admin
from django.utils.safestring import mark_safe
from django.utils.translation import ugettext_lazy as _

from apps.account.models import User
from .models import Category, Restaurant, RestaurantTable, Payable


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
    list_display = (
        "name",
        "view_food_items",
        "email_address",
        "phone_number",
        "is_public",
    )
    search_fields = ("user__name", "user__email_address", "user__phone_number")
    list_filter = ("is_public", "user__name")

    def view_food_items(self, obj):
        return mark_safe(f"<a href='/admin/food/fooditem/?q={obj.user.id}'>View</a>")

    view_food_items.short_description = _("Food Items")
    view_food_items.allow_tags = True

    def name(self, obj):
        return obj.user.name

    def email_address(self, obj):
        return obj.user.email

    def phone_number(self, obj):
        return obj.user.phone_number


@admin.register(Payable)
class PayableAdmin(admin.ModelAdmin):
    list_display = (
        "name",
        "phone_number",
        "get_inhouse_earning",
        "get_pickup_earning",
        "get_total_earning",
    )

    date_hierarchy = "user__created_at"
    search_fields = ("user__email", "user__phone_number")

    def name(self, obj):
        return obj.user.name

    def phone_number(self, obj):
        return obj.user.phone_number

    def get_inhouse_earning(self, obj):
        return obj.get_inhouse_earning()

    get_inhouse_earning.short_description = "Inhouse earning"

    def get_pickup_earning(self, obj):
        return obj.get_pickup_earning()

    get_pickup_earning.short_description = "Pickup earning"

    def get_total_earning(self, obj):
        return obj.get_total_earning()

    get_total_earning.short_description = "Total earning"

    def has_add_permission(self, request):
        return False

    def has_change_permission(self, request, obj=None):
        return False

    def has_delete_permission(self, request, obj=None):
        return False


@admin.register(RestaurantTable)
class RestaurantTableAdmin(OnlyRestaurantInUserAdmin):
    list_display = ("id", "name", "user", "is_active")
    list_filter = ("is_active",)
    search_fields = ("user__name", "user__phone_number")
    date_hierarchy = "created_at"
