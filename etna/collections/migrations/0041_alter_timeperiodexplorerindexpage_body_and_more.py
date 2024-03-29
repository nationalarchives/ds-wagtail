# Generated by Django 4.1.7 on 2023-04-06 12:18

from django.db import migrations
import wagtail.blocks
import wagtail.fields


class Migration(migrations.Migration):
    dependencies = [
        ("collections", "0040_timeperiodexplorerindexpage_hero_image_and_more"),
    ]

    operations = [
        migrations.AlterField(
            model_name="timeperiodexplorerindexpage",
            name="body",
            field=wagtail.fields.StreamField(
                [
                    (
                        "large_card_links",
                        wagtail.blocks.StructBlock(
                            [
                                (
                                    "heading",
                                    wagtail.blocks.CharBlock(
                                        default="More to explore", max_length=100
                                    ),
                                ),
                                (
                                    "page_1",
                                    wagtail.blocks.PageChooserBlock(
                                        label="Link one target"
                                    ),
                                ),
                                (
                                    "page_2",
                                    wagtail.blocks.PageChooserBlock(
                                        label="Link two target"
                                    ),
                                ),
                            ]
                        ),
                    )
                ],
                blank=True,
                use_json_field=True,
            ),
        ),
        migrations.AlterField(
            model_name="topicexplorerindexpage",
            name="body",
            field=wagtail.fields.StreamField(
                [
                    (
                        "large_card_links",
                        wagtail.blocks.StructBlock(
                            [
                                (
                                    "heading",
                                    wagtail.blocks.CharBlock(
                                        default="More to explore", max_length=100
                                    ),
                                ),
                                (
                                    "page_1",
                                    wagtail.blocks.PageChooserBlock(
                                        label="Link one target"
                                    ),
                                ),
                                (
                                    "page_2",
                                    wagtail.blocks.PageChooserBlock(
                                        label="Link two target"
                                    ),
                                ),
                            ]
                        ),
                    )
                ],
                blank=True,
                use_json_field=True,
            ),
        ),
    ]
