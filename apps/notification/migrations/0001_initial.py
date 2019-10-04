# Generated by Django 2.2.5 on 2019-10-04 11:56

from django.conf import settings
import django.contrib.postgres.fields.jsonb
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Action',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('message', models.CharField(max_length=300)),
                ('message_in_ar', models.CharField(max_length=300)),
                ('action_type', models.CharField(choices=[('RESTAURANT_NEW_TABLE_ORDER', 'New Table Order'), ('RESTAURANT_NEW_PICKUP_ORDER', 'New Pickup Order'), ('RESTAURANT_NEW_ITEM_IN_ORDER', 'New Item In Order'), ('RESTAURANT_CHECKOUT_FROM_ORDER', 'Checkout From Order'), ('RESTAURANT_RECEIVED_PAYMENT_FOR_ORDER', 'Received Payment For Order'), ('RESTAURANT_TICKET_RESPONSE_FROM_ADMIN', 'Ticket Response From Admin'), ('RESTAURANT_TICKET_CLOSED_BY_ADMIN', 'Ticket Closed By Admin')], max_length=100)),
                ('extra_data', django.contrib.postgres.fields.jsonb.JSONField(null=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('sender', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='notification_sender', to=settings.AUTH_USER_MODEL)),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='notification_user', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'ordering': ('-created_at',),
            },
        ),
    ]
