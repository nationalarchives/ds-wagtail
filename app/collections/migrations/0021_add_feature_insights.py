# Generated by Django 3.2.13 on 2022-06-20 20:00
# etna:allowAlterField

from django.db import migrations, models
import django.db.models.deletion
import wagtail.blocks
import wagtail.fields


class Migration(migrations.Migration):
    dependencies = [
        ("articles", "0042_alter_insightspage_body"),
        ("collections", "0020_rename_result_page_record_relationship"),
    ]

    operations = [
        migrations.AddField(
            model_name="timeperiodexplorerpage",
            name="featured_insight",
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.SET_NULL,
                to="articles.insightspage",
            ),
        ),
        migrations.AddField(
            model_name="topicexplorerpage",
            name="featured_insight",
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.SET_NULL,
                to="articles.insightspage",
            ),
        ),
        migrations.AlterField(
            model_name="timeperiodexplorerpage",
            name="body",
            field=wagtail.fields.StreamField(
                [
                    (
                        "collection_highlights",
                        wagtail.blocks.StructBlock(
                            [
                                (
                                    "heading",
                                    wagtail.blocks.CharBlock(
                                        default="Collection Highlights", max_length=100
                                    ),
                                )
                            ]
                        ),
                    ),
                    (
                        "promoted_pages",
                        wagtail.blocks.StructBlock(
                            [
                                (
                                    "heading",
                                    wagtail.blocks.CharBlock(max_length=100),
                                ),
                                (
                                    "sub_heading",
                                    wagtail.blocks.CharBlock(max_length=200),
                                ),
                                (
                                    "promoted_items",
                                    wagtail.blocks.ListBlock(
                                        wagtail.blocks.TextBlock,
                                        max=3,
                                        min=3,
                                    ),
                                ),
                            ]
                        ),
                    ),
                ],
                blank=True,
            ),
        ),
        migrations.AlterField(
            model_name="topicexplorerpage",
            name="body",
            field=wagtail.fields.StreamField(
                [
                    (
                        "collection_highlights",
                        wagtail.blocks.StructBlock(
                            [
                                (
                                    "heading",
                                    wagtail.blocks.CharBlock(
                                        default="Collection Highlights", max_length=100
                                    ),
                                )
                            ]
                        ),
                    ),
                    (
                        "promoted_pages",
                        wagtail.blocks.StructBlock(
                            [
                                (
                                    "heading",
                                    wagtail.blocks.CharBlock(max_length=100),
                                ),
                                (
                                    "sub_heading",
                                    wagtail.blocks.CharBlock(max_length=200),
                                ),
                                (
                                    "promoted_items",
                                    wagtail.blocks.ListBlock(
                                        wagtail.blocks.TextBlock,
                                        max=3,
                                        min=3,
                                    ),
                                ),
                            ]
                        ),
                    ),
                ],
                blank=True,
            ),
        ),
    ]
