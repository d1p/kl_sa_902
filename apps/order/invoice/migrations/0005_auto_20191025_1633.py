# Generated by Django 2.2.5 on 2019-10-25 16:33

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('invoice', '0004_auto_20191023_1429'),
    ]

    operations = [
        migrations.AlterField(
            model_name='transaction',
            name='transaction_status',
            field=models.IntegerField(choices=[(0, 'Pending'), (1, 'Successful'), (2, 'Failed'), (3, 'Invalid'), (5, 'Authorized')], db_index=True, default=0),
        ),
    ]
