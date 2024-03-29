# Generated by Django 4.1.8 on 2023-04-27 11:43

import uuid
from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("core", "0003_set_page_uuid"),
        ("home", "0023_add_page_uuid"),
    ]

    operations = [
        migrations.AlterField(
            model_name="homepage",
            name="uuid",
            field=models.UUIDField(
                default=uuid.uuid4, editable=False, unique=True, verbose_name="UUID"
            ),
        ),
    ]
