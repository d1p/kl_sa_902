# Generated by Django 2.2.8 on 2020-01-13 12:46

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ("ticket", "0006_customerticket_customertickettopic"),
    ]

    operations = [
        migrations.AlterField(
            model_name="restaurantmessage",
            name="ticket",
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.CASCADE,
                related_name="messages",
                to="ticket.RestaurantTicket",
            ),
        ),
    ]
