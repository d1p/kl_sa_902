from django.utils.translation import ugettext_lazy as _


class OrderType:
    PICK_UP = 0
    IN_HOUSE = 2

    CHOICES = ((PICK_UP, _("Pick Up")), (IN_HOUSE, _("In House")))


class OrderStatusType:
    CLOSED = 0
    OPEN = 1
    CHECKOUT = 2
    COMPLETED = 3

    CHOICES = (
        (CLOSED, _("Closed")),
        (OPEN, _("Open"))
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
        (REJECTED, _("Rejected"))
    )
