# Generated by Django 2.2.5 on 2019-11-21 03:20

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('customer', '0006_auto_20191121_0208'),
    ]

    operations = [
        migrations.AlterField(
            model_name='misc',
            name='state',
            field=models.CharField(choices=[('No Order', 'No Order'), ('IN_ORDER', 'In Order'), ('IN_CHECKOUT', 'In Checkout'), ('IN_RATING', 'In Rating')], db_index=True, default='IN_ORDER', max_length=40),
        ),
    ]
