# Generated by Django 2.2.4 on 2019-08-14 19:58

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('restaurant', '0004_auto_20190814_1951'),
    ]

    operations = [
        migrations.AlterField(
            model_name='restaurant',
            name='full_address',
            field=models.TextField(blank=True, db_index=True, max_length=800),
        ),
        migrations.AlterField(
            model_name='restaurant',
            name='restaurant_type',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='restaurant.Category'),
        ),
    ]
