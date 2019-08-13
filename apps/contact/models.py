from django.db import models

from apps.account.models import User


class ContactGroup(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, db_index=True)
    name = models.CharField(max_length=255)
    contacts = models.ManyToManyField(User, related_name="contacts", db_index=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ("user", "name",)

    def __str__(self):
        return f"{self.user.name}s group containing {self.contacts.count()} members."
