# Generated by Django 4.2.1 on 2023-05-23 16:43
# etna:allowAlterField

from django.db import migrations
import wagtail.blocks
import wagtail.fields


class Migration(migrations.Migration):
    dependencies = [
        ("articles", "0084_alter_articlepage_body"),
    ]

    operations = [
        migrations.AlterField(
            model_name="recordarticlepage",
            name="promoted_links",
            field=wagtail.fields.StreamField(
                [
                    (
                        "promoted_link",
                        wagtail.blocks.StructBlock(
                            [
                                ("heading", wagtail.blocks.CharBlock(max_length=100)),
                                (
                                    "promoted_items",
                                    wagtail.blocks.ListBlock(
                                        wagtail.blocks.TextBlock(),
                                        max_num=3,
                                    ),
                                ),
                            ]
                        ),
                    )
                ],
                blank=True,
                null=True,
                use_json_field=True,
            ),
        ),
    ]
