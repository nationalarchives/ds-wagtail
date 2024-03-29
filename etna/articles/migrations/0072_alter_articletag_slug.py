# Generated by Django 4.1.8 on 2023-04-06 09:46

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("articles", "0071_recordarticlepage_promoted_links"),
    ]

    operations = [
        migrations.AlterField(
            model_name="articletag",
            name="slug",
            field=models.SlugField(
                allow_unicode=True, max_length=100, unique=True, verbose_name="slug"
            ),
        ),
    ]
