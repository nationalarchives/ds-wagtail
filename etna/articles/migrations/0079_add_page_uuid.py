# Generated by Django 4.1.8 on 2023-04-27 10:58

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("articles", "0078_alter_articletag_skos_id"),
    ]

    operations = [
        migrations.AddField(
            model_name="articleindexpage",
            name="uuid",
            field=models.UUIDField(null=True),
        ),
        migrations.AddField(
            model_name="articlepage",
            name="uuid",
            field=models.UUIDField(null=True),
        ),
        migrations.AddField(
            model_name="recordarticlepage",
            name="uuid",
            field=models.UUIDField(null=True),
        ),
    ]
