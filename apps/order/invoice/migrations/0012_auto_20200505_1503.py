# Generated by Django 2.2.12 on 2020-05-05 15:03

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ("order", "0020_auto_20200401_1555"),
        ("invoice", "0011_paymentsnapshots"),
    ]

    operations = [
        migrations.RenameModel(
            old_name="PaymentSnapshots", new_name="PaymentSnapshot",
        ),
    ]
