from django.db import models
from django.utils.translation import ugettext_lazy as _

from apps.account.models import User
from utils.file import RandomFileName


class FoodCategory(models.Model):
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, db_index=True)
    name = models.CharField(max_length=266, db_index=True)
    created_at = models.DateTimeField(auto_now_add=True)
    is_deleted = models.BooleanField(default=False, db_index=True)

    class Meta:
        verbose_name = _("Category")
        verbose_name_plural = _("Categories")

    def __str__(self):
        return f"{self.name} by {self.user.name}"


class FoodItem(models.Model):
    category = models.ForeignKey(FoodCategory, on_delete=models.SET_NULL, null=True)
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, db_index=True)
    name = models.CharField(max_length=300, db_index=True)
    picture = models.ImageField(
        upload_to=RandomFileName("user/restaurant/food/"),
        default="user/restaurant/food/default.png",
    )
    price = models.DecimalField(max_digits=9, decimal_places=2)
    calorie = models.IntegerField()
    is_active = models.BooleanField(default=False, db_index=True)
    is_deleted = models.BooleanField(default=False, db_index=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name


class FoodAttribute(models.Model):
    name = models.CharField(max_length=144)
    food = models.ForeignKey(FoodItem, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ("name",)

    def __str__(self):
        return self.name


class FoodAttributeMatrix(models.Model):
    name = models.CharField(max_length=144)
    attribute = models.ForeignKey(FoodAttribute, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ("name",)

    def __str__(self):
        return self.name


class FoodAddOn(models.Model):
    food = models.ForeignKey(FoodItem, on_delete=models.CASCADE)
    name = models.CharField(max_length=144, db_index=True)
    price = models.DecimalField(max_digits=9, decimal_places=2)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ("name",)

    def __str__(self):
        return self.name
