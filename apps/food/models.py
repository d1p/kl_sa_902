from django.db import models
from django.utils.translation import ugettext_lazy as _

from apps.account.models import User


class FoodCategory(models.Model):
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, db_index=True)
    name = models.CharField(max_length=266, db_index=True)
    created_at = models.DateTimeField(auto_now_add=True)
    is_active = models.BooleanField(default=True, db_index=True)

    class Meta:
        verbose_name = _("Category")
        verbose_name_plural = _("Categories")

    def __str__(self):
        return f"{self.name} by {self.user.name}"
