# Generated by Django 5.0.8 on 2024-08-20 10:03

import django.db.models.deletion
import modelcluster.fields
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("images", "0009_alter_customimage_custom_sensitive_image_warning"),
        ("people", "0011_alter_personpage_role_alter_personpage_summary"),
    ]

    operations = [
        migrations.CreateModel(
            name="ShopItem",
            fields=[
                (
                    "id",
                    models.AutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("title", models.CharField(max_length=255)),
                ("url", models.URLField()),
                ("price", models.DecimalField(decimal_places=2, max_digits=6)),
                (
                    "image",
                    models.ForeignKey(
                        null=True,
                        on_delete=django.db.models.deletion.SET_NULL,
                        related_name="+",
                        to="images.customimage",
                    ),
                ),
                (
                    "page",
                    modelcluster.fields.ParentalKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="shop_items",
                        to="people.personpage",
                    ),
                ),
            ],
            options={
                "verbose_name": "Shop item",
                "verbose_name_plural": "Shop items",
            },
        ),
    ]