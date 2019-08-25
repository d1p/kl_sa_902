from django.contrib import admin

from apps.account.models import User
from .models import FoodCategory


@admin.register(FoodCategory)
class FoodCategoryAdmin(admin.ModelAdmin):
    list_display = ("id", "name", "user", "is_active", "created_at")
    list_filter = ("is_active",)
    search_fields = ("user__name",)
    date_hierarchy = "created_at"

    def get_form(self, request, obj=None, **kwargs):
        # Override the form so that only real restaurants which are public can be shown in the user      field. if already
        # exists then hide others.
        form = super(FoodCategoryAdmin, self).get_form(request, obj, **kwargs)
        if obj is None:
            form.base_fields["user"].queryset = User.objects.filter(
                groups__name="Restaurant", restaurant__is_public=True
            )
        else:
            form.base_fields["user"].queryset = User.objects.filter(id=obj.user.id)
        form.base_fields["user"].widget.can_add_related = False
        return form
