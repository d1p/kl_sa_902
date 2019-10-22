# Generated by Django 2.2.5 on 2019-10-21 17:40

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('customer', '0004_misc_last_order_in_checkout'),
    ]

    operations = [
        migrations.AddField(
            model_name='misc',
            name='last_order_type',
            field=models.IntegerField(null=True),
        ),
        migrations.AddField(
            model_name='misc',
            name='last_restaurant',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, related_name='last_restaurant_user', to=settings.AUTH_USER_MODEL),
        ),
    ]