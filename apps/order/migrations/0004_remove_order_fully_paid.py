# Generated by Django 2.2.5 on 2019-09-13 07:09

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('order', '0003_auto_20190911_1420'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='order',
            name='fully_paid',
        ),
    ]