# Generated by Django 2.2.4 on 2019-08-25 04:03

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [("food", "0003_auto_20190825_0156")]

    operations = [
        migrations.AddField(
            model_name="foodattributematrix",
            name="food",
            field=models.ForeignKey(
                default=1,
                on_delete=django.db.models.deletion.CASCADE,
                to="food.FoodItem",
            ),
            preserve_default=False,
        )
    ]
