# Generated by Django 4.0.8 on 2022-10-31 10:45

from django.db import migrations, models
import django.db.models.deletion
import app.core.blocks.page_list
import wagtail.blocks
import wagtail.fields


class Migration(migrations.Migration):
    dependencies = [
        ("articles", "0045_add_search_image_fields"),
        ("home", "0011_add_search_image_fields"),
    ]

    operations = [
        migrations.AddField(
            model_name="homepage",
            name="featured_collections",
            field=wagtail.fields.StreamField(
                [
                    (
                        "featuredcollection",
                        wagtail.blocks.StructBlock(
                            [
                                (
                                    "items",
                                    app.core.blocks.page_list.PageListBlock(
                                        "articles.InsightsPage", max_num=9, min_num=3
                                    ),
                                )
                            ]
                        ),
                    )
                ],
                blank=True,
                null=True,
                use_json_field=True,
            ),
        ),
        migrations.AddField(
            model_name="homepage",
            name="featured_insight",
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.SET_NULL,
                to="articles.insightspage",
            ),
        ),
        migrations.AddField(
            model_name="homepage",
            name="sub_heading",
            field=models.CharField(
                default="Discover some of the most important and unusual records from over 1000 years of history.",
                max_length=255,
            ),
        ),
        migrations.AlterField(
            model_name="homepage",
            name="body",
            field=wagtail.fields.StreamField(
                [
                    (
                        "time_period",
                        wagtail.blocks.StructBlock(
                            [
                                (
                                    "heading",
                                    wagtail.blocks.CharBlock(
                                        default="Explore by time period", max_length=100
                                    ),
                                ),
                                (
                                    "sub_heading",
                                    wagtail.blocks.CharBlock(
                                        default="Discover 1,000 years of British history through time periods including:",
                                        max_length=200,
                                    ),
                                ),
                                (
                                    "page",
                                    wagtail.blocks.PageChooserBlock(
                                        page_type=[
                                            "collections.TimePeriodExplorerIndexPage"
                                        ]
                                    ),
                                ),
                            ]
                        ),
                    ),
                    (
                        "topic_explorer",
                        wagtail.blocks.StructBlock(
                            [
                                (
                                    "heading",
                                    wagtail.blocks.CharBlock(
                                        default="Explore by topic", max_length=100
                                    ),
                                ),
                                (
                                    "sub_heading",
                                    wagtail.blocks.CharBlock(
                                        default="Browse highlights of the collection through topics including:",
                                        max_length=200,
                                    ),
                                ),
                                (
                                    "page",
                                    wagtail.blocks.PageChooserBlock(
                                        page_type=["collections.TopicExplorerIndexPage"]
                                    ),
                                ),
                            ]
                        ),
                    ),
                    (
                        "paragraph",
                        wagtail.blocks.StructBlock(
                            [
                                (
                                    "text",
                                    wagtail.blocks.RichTextBlock(
                                        features=["bold", "italic", "link", "ul"]
                                    ),
                                )
                            ]
                        ),
                    ),
                    (
                        "paragraph_with_heading",
                        wagtail.blocks.StructBlock(
                            [
                                (
                                    "heading_level",
                                    wagtail.blocks.ChoiceBlock(
                                        choices=[
                                            ("h2", "Heading level 2"),
                                            ("h3", "Heading level 3"),
                                            ("h4", "Heading level 4"),
                                        ],
                                        help_text="Use this field to select the appropriate heading tag. Check where this component will sit in the page to ensure that it follows the correct heading order and avoids skipping levels e.g. an &lt;h4&gt; should not follow an &lt;h2&gt;. For further information, see: <a href=https://www.w3.org/WAI/tutorials/page-structure/headings target=_blank>https://www.w3.org/WAI/tutorials/page-structure/headings/</a>",
                                    ),
                                ),
                                (
                                    "heading",
                                    wagtail.blocks.CharBlock(
                                        max_length=100, required=True
                                    ),
                                ),
                                (
                                    "paragraph",
                                    wagtail.blocks.RichTextBlock(
                                        features=["bold", "italic", "link", "ul"],
                                        required=True,
                                    ),
                                ),
                            ]
                        ),
                    ),
                ],
                blank=True,
                null=True,
                use_json_field=True,
            ),
        ),
    ]
