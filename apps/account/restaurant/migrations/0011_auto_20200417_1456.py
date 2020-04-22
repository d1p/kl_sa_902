# Generated by Django 2.2.12 on 2020-04-17 14:56

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("restaurant", "0010_restaurant_tax_percentage"),
    ]

    operations = [
        migrations.AddField(
            model_name="restaurant",
            name="inhouse_earning",
            field=models.DecimalField(decimal_places=3, default=0.0, max_digits=6),
        ),
        migrations.AddField(
            model_name="restaurant",
            name="pickup_earning",
            field=models.DecimalField(decimal_places=3, default=0.0, max_digits=6),
        ),
        migrations.AddField(
            model_name="restaurant",
            name="total_earning",
            field=models.DecimalField(decimal_places=3, default=0.0, max_digits=6),
        ),
    ]
