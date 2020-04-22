from django.contrib import admin

from apps.account.models import User
from .models import Customer, Misc


@admin.register(Misc)
class MiscAdmin(admin.ModelAdmin):
    list_display = ("name", "phone_number", "state")
    search_fields = ("user__phone_number", "user__name")

    def name(self, obj):
        return obj.user.name

    def phone_number(self, obj):
        return obj.user.phone_number


class CustomerInline(admin.TabularInline):
    def __init__(self, *args, **kwargs):
        super(CustomerInline, self).__init__(*args, **kwargs)
        self.can_delete = False

    model = Customer


class CustomerAdmin(admin.ModelAdmin):
    search_fields = ("user__email", "user__name", "user__phone_number")
    list_display = ("email_address", "name", "phone_number")
    date_hierarchy = "user__created_at"

    def name(self, obj):
        return obj.user.name

    def email_address(self, obj):
        return obj.user.email

    def phone_number(self, obj):
        return obj.user.phone_number

    def get_form(self, request, obj=None, **kwargs):
        form = super(CustomerAdmin, self).get_form(request, obj, **kwargs)

        form.base_fields["user"].queryset = User.objects.filter(
            customer=obj, is_staff=False, is_superuser=False
        )
        form.base_fields["user"].widget.can_add_related = True
        return form


admin.site.register(Customer, CustomerAdmin)
