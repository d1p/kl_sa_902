from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.utils.translation import ugettext_lazy as _

from apps.account.customer.admin import CustomerInline
from apps.account.restaurant.admin import RestaurantInline
from apps.account.types import ProfileType
from .models import User, VerifyPhoneToken, ForgotPasswordToken, ChangePhoneNumberToken


@admin.register(User)
class CustomUserAdmin(UserAdmin):
    fieldsets = (
        (
            None,
            {
                "fields": (
                    "name",
                    "email",
                    "phone_number",
                    "password",
                    "profile_picture",
                    "locale",
                    "is_active",
                )
            },
        ),
        (_("Important dates"), {"fields": ("last_login",)}),
    )
    add_fieldsets = (
        (
            None,
            {
                "classes": ("wide",),
                "fields": (
                    "name",
                    "email",
                    "phone_number",
                    "password1",
                    "password2",
                    "is_active",
                    "is_staff",
                    "is_superuser",
                ),
            },
        ),
    )

    list_display = (
        "id",
        "name",
        "email",
        "phone_number",
        "is_active",
        "is_staff",
        "is_superuser",
        "profile_type",
    )
    search_fields = ("id", "email", "phone_number", "name")
    ordering = ("id", "is_staff", "is_superuser")
    extra = 0

    def get_inline_instances(self, request, obj=None):
        try:
            if obj.profile_type is ProfileType.CUSTOMER:
                inline = [CustomerInline]
            elif obj.profile_type is ProfileType.RESTAURANT:
                inline = [RestaurantInline]
            else:
                inline = []
        except:
            inline = []

        self.inlines = inline
        return super(UserAdmin, self).get_inline_instances(request, obj)

    def get_fieldsets(self, request, obj=None):
        fieldsets = super(CustomUserAdmin, self).get_fieldsets(request, obj)
        if obj is None:
            fieldsets += (
                (
                    _("Permissions"),
                    {
                        "fields": (
                            "is_staff",
                            "is_superuser",
                            "groups",
                            "user_permissions",
                        )
                    },
                ),
            )
        else:
            if (
                obj.profile_type != ProfileType.CUSTOMER
                and obj.profile_type != ProfileType.RESTAURANT
            ):
                fieldsets += (
                    (
                        _("Permissions"),
                        {
                            "fields": (
                                "is_active",
                                "is_staff",
                                "is_superuser",
                                "groups",
                                "user_permissions",
                            )
                        },
                    ),
                )
        return fieldsets


admin.site.register(VerifyPhoneToken)
admin.site.register(ForgotPasswordToken)
admin.site.register(ChangePhoneNumberToken)
