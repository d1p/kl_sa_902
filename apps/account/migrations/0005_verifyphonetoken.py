# Generated by Django 2.2.4 on 2019-08-11 06:39

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [("account", "0004_auto_20190809_1144")]

    operations = [
        migrations.CreateModel(
            name="VerifyPhoneToken",
            fields=[
                (
                    "token_ptr",
                    models.OneToOneField(
                        auto_created=True,
                        on_delete=django.db.models.deletion.CASCADE,
                        parent_link=True,
                        primary_key=True,
                        serialize=False,
                        to="account.Token",
                    ),
                )
            ],
            bases=("account.token",),
        )
    ]
