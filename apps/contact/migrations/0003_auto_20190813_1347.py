# Generated by Django 2.2.4 on 2019-08-13 13:47

from django.conf import settings
from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ("contact", "0002_contactgroup_name"),
    ]

    operations = [
        migrations.AlterUniqueTogether(
            name="contactgroup", unique_together={("user", "name")}
        )
    ]
