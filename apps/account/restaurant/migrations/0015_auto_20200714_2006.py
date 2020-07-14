# Generated by Django 2.2.12 on 2020-07-14 17:06

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('restaurant', '0014_auto_20200714_1954'),
    ]

    operations = [
        migrations.AlterField(
            model_name='restaurant',
            name='app_inhouse_earning',
            field=models.DecimalField(decimal_places=3, default=0.0, max_digits=15),
        ),
        migrations.AlterField(
            model_name='restaurant',
            name='app_pickup_earning',
            field=models.DecimalField(decimal_places=3, default=0.0, max_digits=15),
        ),
        migrations.AlterField(
            model_name='restaurant',
            name='app_total_earning',
            field=models.DecimalField(decimal_places=3, default=0.0, max_digits=15),
        ),
        migrations.AlterField(
            model_name='restaurant',
            name='inhouse_earning',
            field=models.DecimalField(decimal_places=3, default=0.0, max_digits=15),
        ),
        migrations.AlterField(
            model_name='restaurant',
            name='pickup_earning',
            field=models.DecimalField(decimal_places=3, default=0.0, max_digits=15),
        ),
        migrations.AlterField(
            model_name='restaurant',
            name='total',
            field=models.DecimalField(decimal_places=3, default=0.0, max_digits=15),
        ),
    ]
