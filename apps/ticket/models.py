from django.db import models
from django.utils.translation import ugettext_lazy as _
from django_extensions.db.fields import ShortUUIDField

from apps.account.models import User


class PreBackedTicketTopic(models.Model):
    text = models.TextField(max_length=300)
    text_in_ar = models.TextField(max_length=300, verbose_name="Text in arabic")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ("text", "text_in_ar")

    def __str__(self):
        return f"{self.text}"


class Ticket(models.Model):
    OPEN = 0
    CLOSED = 1

    STATUSES = ((OPEN, _("Open")), (CLOSED, _("Closed")))

    id = ShortUUIDField(primary_key=True)
    created_by = models.ForeignKey(
        User, db_index=True, on_delete=models.SET_NULL, null=True
    )
    topic = models.CharField(max_length=300, help_text=_("Topic Name"))
    description = models.TextField(max_length=1000)
    status = models.IntegerField(choices=STATUSES, default=OPEN)
    created_at = models.DateTimeField(auto_now_add=True)
    last_updated = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ("-last_updated",)
        verbose_name = _("Ticket")
        verbose_name_plural = _("Tickets")

    def __str__(self):
        return f"{self.created_by}: {self.topic}"


class Message(models.Model):
    ticket = models.ForeignKey(Ticket, on_delete=models.CASCADE, db_index=True)
    sender = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    text = models.TextField(max_length=5000)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ("-created_at",)
        verbose_name = _("Message")
        verbose_name_plural = _("Messages")

    def __str__(self):
        return f"{self.ticket}: {self.text} at {self.created_at}"
