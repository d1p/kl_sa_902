# Generated by Django 2.2.8 on 2020-04-02 05:37

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("account", "0016_auto_20200122_1630"),
    ]

    operations = [
        migrations.AddField(
            model_name="user",
            name="name_in_ar",
            field=models.CharField(
                blank=True, help_text="Name in arabic", max_length=50, null=True
            ),
        ),
    ]
