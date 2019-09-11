from django.db import models
from django.utils.translation import ugettext_lazy as _
from apps.account.models import User
from django.contrib.postgres.fields import JSONField


class Notification(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCASE, db_index=True)
    sender = models.ForeignKey(User, on_delete=models.CASCADE)
    message = models.CharField(max_length=300)
    message_in_ar = models.CharField(max_length=300)
    action_type = models.IntegerField()
    extra_data = JSONField(null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ("-created_at",)

    def sender_profile_picture(self):
        return self.sender.profile_picture.url

    def sender_name(self):
        return self.sender.name
        
