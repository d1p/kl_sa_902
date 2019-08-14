from django.contrib.gis.db.models import PointField
from django.contrib.gis.geos import Point
from django.db import models
from django.utils.translation import ugettext_lazy as _

from apps.account.models import User
from utils.file import RandomFileName


class Category(models.Model):
    name = models.CharField(max_length=45, unique=True, db_index=True)
    name_in_ar = models.CharField(
        _("Name in Arabic"), max_length=45, unique=True, db_index=True
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = _("Category")
        verbose_name_plural = _("Categories")

    def __str__(self):
        return f"{self.name} {self.name_in_ar}"


class Restaurant(models.Model):
    user = models.OneToOneField(User, db_index=True, on_delete=models.CASCADE)
    cover_picture = models.ImageField(
        upload_to=RandomFileName("user/restaurant/cover/"),
        default="user/restaurant/cover/default.png",
    )
    restaurant_type = models.ForeignKey(
        Category, on_delete=models.SET_NULL, null=True, blank=False, db_index=True
    )
    full_address = models.TextField(max_length=800, db_index=True)
    geolocation = PointField(
        spatial_index=True, srid=4326, null=True, blank=True, editable=False
    )  # Srid 4326 is compatible with google maps.

    lat = models.FloatField()
    lng = models.FloatField()

    online = models.BooleanField(default=False, db_index=True)

    is_public = models.BooleanField(default=False, db_index=True)

    def __str__(self):
        return f"{self.user} - {self.user.name}"

    def clean(self):
        self.geolocation = Point(self.lng, self.lat, srid=4326)


class RestaurantTable(models.Model):
    restaurant = models.ForeignKey(Restaurant, db_index=True, on_delete=models.CASCADE)
    name = models.CharField(max_length=100)
    qr_code = models.ImageField(upload_to=RandomFileName("user/restaurant/table"))
    created_at = models.DateTimeField(auto_now_add=True)
    is_active = models.BooleanField(default=True, db_index=True)

    def __str__(self):
        return f"{self.name} by {self.restaurant.user.name}"
