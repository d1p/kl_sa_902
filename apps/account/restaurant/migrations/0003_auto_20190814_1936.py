# Generated by Django 2.2.4 on 2019-08-14 19:36

from django.db import migrations, models
import django.db.models.deletion
import utils.file


class Migration(migrations.Migration):

    dependencies = [("restaurant", "0002_auto_20190812_1456")]

    operations = [
        migrations.AddField(
            model_name="restaurant",
            name="is_public",
            field=models.BooleanField(db_index=True, default=False),
        ),
        migrations.CreateModel(
            name="RestaurantTable",
            fields=[
                (
                    "id",
                    models.AutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("name", models.CharField(max_length=100)),
                (
                    "qr_code",
                    models.ImageField(
                        upload_to=utils.file.RandomFileName("user/restaurant/table")
                    ),
                ),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("is_active", models.BooleanField(db_index=True, default=True)),
                (
                    "restaurant",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        to="restaurant.Restaurant",
                    ),
                ),
            ],
        ),
    ]
