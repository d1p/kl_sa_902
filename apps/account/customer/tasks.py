from io import BytesIO

import qrcode

from apps.account.customer.models import Customer
from conf.celery import app
