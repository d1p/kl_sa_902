from django.contrib.postgres.fields import JSONField
from django.db import models

from apps.account.models import User
from .types import NotificationActionType


class Action(models.Model):
    user = models.ForeignKey(
        User, on_delete=models.CASCADE, db_index=True, related_name="notification_user"
    )
    sender = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="notification_sender", null=True, blank=True
    )
    message = models.CharField(max_length=300)
    message_in_ar = models.CharField(max_length=300)
    action_type = models.CharField(
        max_length=100, choices=NotificationActionType.CHOICES
    )
    extra_data = JSONField(null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ("-created_at",)


    def sender_name(self):
        if self.sender is not None:
            return self.sender.name
        else:
            return ""
