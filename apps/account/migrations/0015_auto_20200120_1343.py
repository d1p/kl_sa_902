# Generated by Django 2.2.8 on 2020-01-20 13:43

import django.core.validators
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('account', '0014_auto_20191207_1015'),
    ]

    operations = [
        migrations.AlterField(
            model_name='changephonenumbertoken',
            name='new_phone_number',
            field=models.CharField(db_index=True, max_length=17, validators=[django.core.validators.RegexValidator(message="Phone number must be entered in the format: '+999999999'. Up to 15 digits allowed.", regex='^\\+?1?\\d{10,15}$')]),
        ),
        migrations.AlterField(
            model_name='changephonenumbertoken',
            name='old_phone_number',
            field=models.CharField(db_index=True, max_length=17, validators=[django.core.validators.RegexValidator(message="Phone number must be entered in the format: '+999999999'. Up to 15 digits allowed.", regex='^\\+?1?\\d{10,15}$')]),
        ),
        migrations.AlterField(
            model_name='user',
            name='phone_number',
            field=models.CharField(max_length=17, unique=True, validators=[django.core.validators.RegexValidator(message="Phone number must be entered in the format: '+999999999'. Up to 15 digits allowed.", regex='^\\+?1?\\d{10,15}$')]),
        ),
    ]
