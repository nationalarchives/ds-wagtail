# Generated by Django 4.1.8 on 2023-04-27 11:43

from django.db import migrations, models
import uuid


class Migration(migrations.Migration):
    dependencies = [
        ("core", "0003_set_page_uuid"),
        ("articles", "0079_add_page_uuid"),
    ]

    operations = [
        migrations.AlterField(
            model_name="articleindexpage",
            name="uuid",
            field=models.UUIDField(
                default=uuid.uuid4, editable=False, unique=True, verbose_name="UUID"
            ),
        ),
        migrations.AlterField(
            model_name="articlepage",
            name="uuid",
            field=models.UUIDField(
                default=uuid.uuid4, editable=False, unique=True, verbose_name="UUID"
            ),
        ),
        migrations.AlterField(
            model_name="recordarticlepage",
            name="uuid",
            field=models.UUIDField(
                default=uuid.uuid4, editable=False, unique=True, verbose_name="UUID"
            ),
        ),
    ]
