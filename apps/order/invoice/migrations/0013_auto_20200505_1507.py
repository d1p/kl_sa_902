# Generated by Django 2.2.12 on 2020-05-05 15:07

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("invoice", "0012_auto_20200505_1503"),
    ]

    operations = [
        migrations.AddField(
            model_name="invoice",
            name="app_earning",
            field=models.DecimalField(decimal_places=3, max_digits=8, null=True),
        ),
        migrations.AddField(
            model_name="invoice",
            name="restaurant_earning",
            field=models.DecimalField(decimal_places=3, max_digits=8, null=True),
        ),
        migrations.DeleteModel(name="PaymentSnapshot",),
    ]
