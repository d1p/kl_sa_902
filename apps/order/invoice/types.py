from django.utils.translation import ugettext_lazy as _


class PaymentStatus:
    PENDING = 0
    SUCCESSFUL = 1
    FAILED = 2
    INVALID = 3
    AUTHORIZED = 5

    CHOICES = (
        (PENDING, _("Pending")),
        (SUCCESSFUL, _("Successful")),
        (FAILED, _("Failed")),
        (INVALID, _("Invalid")),
        (AUTHORIZED, _("Authorized")),
    )
