from django.utils.translation import ugettext_lazy as _


class CustomerMiscType:
    NO_ORDER = "No Order"
    IN_ORDER = "IN_ORDER"
    IN_CHECKOUT = "IN_CHECKOUT"
    IN_RATING = "IN_RATING"

    choices = (
        (NO_ORDER, _("No Order")),
        (IN_ORDER, _("In Order")),
        (IN_CHECKOUT, _("In Checkout")),
        (IN_RATING, _("In Rating")),
    )
