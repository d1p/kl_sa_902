# Generated by Django 2.2.4 on 2019-08-29 08:09

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('food', '0005_remove_foodattributematrix_food'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='foodcategory',
            name='is_active',
        ),
        migrations.AddField(
            model_name='foodcategory',
            name='is_deleted',
            field=models.BooleanField(db_index=True, default=False),
        ),
        migrations.AddField(
            model_name='fooditem',
            name='is_deleted',
            field=models.BooleanField(db_index=True, default=False),
        ),
    ]
