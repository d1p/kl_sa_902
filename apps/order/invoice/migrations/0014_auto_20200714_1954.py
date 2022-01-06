# Generated by Django 2.2.12 on 2020-07-14 16:54

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('invoice', '0013_auto_20200505_1507'),
    ]

    operations = [
        migrations.AlterField(
            model_name='invoice',
            name='app_earning',
            field=models.DecimalField(decimal_places=3, max_digits=9, null=True),
        ),
        migrations.AlterField(
            model_name='invoice',
            name='restaurant_earning',
            field=models.DecimalField(decimal_places=3, max_digits=9, null=True),
        ),
    ]