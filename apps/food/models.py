from django.db import models
from

class Category(models.DateTimeField):
    name = models.CharField(max_length=266, db_index=True)
    created_at = models.DateTimeField(auto_now_add=True)
