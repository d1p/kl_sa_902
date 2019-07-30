from django.db import models
from apps.account.models import User


class Customer(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    qr_code = models.ImageField()
