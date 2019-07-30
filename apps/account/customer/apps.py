from django.apps import AppConfig
from django.utils.translation import ugettext_lazy as _


class CustomerConfig(AppConfig):
    name = "apps.account.customer"
    verbose_name = _("Customer")

    def ready(self):
        pass
