# Generated by Django 2.2.4 on 2019-09-03 16:28

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [("food", "0011_auto_20190903_1618")]

    operations = [
        migrations.AddField(
            model_name="foodattribute",
            name="price",
            field=models.DecimalField(
                blank=True, decimal_places=2, max_digits=9, null=True
            ),
        )
    ]
