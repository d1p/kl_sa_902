# Generated by Django 2.2.5 on 2019-11-21 03:20

from decimal import Decimal
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("invoice", "0005_auto_20191025_1633"),
    ]

    operations = [
        migrations.AddField(
            model_name="invoiceitem",
            name="general_amount",
            field=models.DecimalField(
                decimal_places=3,
                default=Decimal("0"),
                help_text="Actual price of the items, without Tax.",
                max_digits=9,
            ),
        ),
        migrations.AddField(
            model_name="invoiceitem",
            name="tax_amount",
            field=models.DecimalField(
                decimal_places=3,
                default=Decimal("0"),
                help_text="Total payable tax amount.",
                max_digits=9,
            ),
        ),
        migrations.AlterField(
            model_name="invoiceitem",
            name="amount",
            field=models.DecimalField(
                decimal_places=3,
                help_text="Actual amount that the user has to pay. With taxing.",
                max_digits=9,
            ),
        ),
    ]
