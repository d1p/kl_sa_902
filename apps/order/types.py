from django.utils.translation import ugettext_lazy as _


class OrderType:
    PICK_UP = 0
    IN_HOUSE = 1

    CHOICES = ((PICK_UP, _("Pick Up")), (IN_HOUSE, _("In House")))


class OrderStatusType:
    OPEN = 1
    CANCELED = 2
    CHECKOUT = 3
    COMPLETED = 4
    IN_PROCESS = 5

    CHOICES = (
        (CANCELED, _("Canceled")),
        (OPEN, _("Open")),
        (CHECKOUT, _("Checkout")),
        (COMPLETED, _("Completed")),
        (IN_PROCESS, _("In Process"))
    )


class OrderItemStatusType:
    UNCONFIRMED = 0
    CONFIRMED = 1

    CHOICES = ((UNCONFIRMED, _("Unconfirmed")), (CONFIRMED, _("Confirmed")))


class OrderInviteStatusType:
    PENDING = 0
    ACCEPTED = 1
    REJECTED = 2

    CHOICES = (
        (PENDING, _("Pending")),
        (ACCEPTED, _("Accepted")),
        (REJECTED, _("Rejected")),
    )
