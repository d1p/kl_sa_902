# Generated by Django 2.2.5 on 2019-09-28 04:37

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('food', '0016_auto_20190923_1542'),
        ('order', '0006_auto_20190928_0435'),
    ]

    operations = [
        migrations.RenameField(
            model_name='orderitemattributematrix',
            old_name='food_attribute',
            new_name='food_attribute_matrix',
        ),
        migrations.AlterUniqueTogether(
            name='orderitemattributematrix',
            unique_together={('order_item', 'food_attribute_matrix')},
        ),
    ]
