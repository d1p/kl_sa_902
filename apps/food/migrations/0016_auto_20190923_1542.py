# Generated by Django 2.2.5 on 2019-09-23 15:42

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('food', '0015_auto_20190922_1756'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='foodaddon',
            name='position',
        ),
        migrations.RemoveField(
            model_name='foodattribute',
            name='position',
        ),
        migrations.RemoveField(
            model_name='foodattributematrix',
            name='position',
        ),
    ]
