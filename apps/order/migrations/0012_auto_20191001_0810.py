# Generated by Django 2.2.5 on 2019-10-01 08:10

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [("order", "0011_auto_20190930_0813")]

    operations = [
        migrations.AddField(
            model_name="order",
            name="confirmed",
            field=models.BooleanField(
                db_index=True,
                default=False,
                help_text="Indicated if an order is confirmed by the users",
            ),
        ),
        migrations.AlterField(
            model_name="order",
            name="status",
            field=models.SmallIntegerField(
                choices=[(2, "Canceled"), (1, "Open"), (3, "Completed")], default=1
            ),
        ),
    ]
