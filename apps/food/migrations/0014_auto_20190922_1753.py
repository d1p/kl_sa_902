# Generated by Django 2.2.5 on 2019-09-22 17:53

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('food', '0013_remove_foodattribute_price'),
    ]

    operations = [
        migrations.AddField(
            model_name='foodaddon',
            name='position',
            field=models.IntegerField(null=True),
        ),
        migrations.AddField(
            model_name='foodattribute',
            name='position',
            field=models.IntegerField(null=True),
        ),
        migrations.AddField(
            model_name='foodattributematrix',
            name='position',
            field=models.IntegerField(null=True),
        ),
    ]