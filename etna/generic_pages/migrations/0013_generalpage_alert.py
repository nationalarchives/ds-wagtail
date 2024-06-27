# Generated by Django 5.0.6 on 2024-06-27 10:35

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("alerts", "0001_initial"),
        ("generic_pages", "0012_alter_generalpage_body"),
    ]

    operations = [
        migrations.AddField(
            model_name="generalpage",
            name="alert",
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.SET_NULL,
                related_name="+",
                to="alerts.alert",
            ),
        ),
    ]