# Generated by Django 2.2.4 on 2019-08-14 19:51

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [("restaurant", "0003_auto_20190814_1936")]

    operations = [
        migrations.AlterField(
            model_name="restaurant",
            name="lat",
            field=models.FloatField(blank=True, null=True),
        ),
        migrations.AlterField(
            model_name="restaurant",
            name="lng",
            field=models.FloatField(blank=True, null=True),
        ),
    ]
