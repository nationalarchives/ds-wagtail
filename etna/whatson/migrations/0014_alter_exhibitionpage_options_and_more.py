# Generated by Django 5.1.2 on 2024-12-02 15:12
# etna:allowRemoveField
# etna:allowAlterField
# etna:allowDeleteModel

import django.core.validators
import django.db.models.deletion
import wagtail.fields
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("images", "0010_alter_customimage_copyright"),
        ("wagtailcore", "0094_alter_page_locale"),
        ("whatson", "0013_remove_eventpage_uuid_remove_exhibitionpage_uuid_and_more"),
    ]

    operations = [
        migrations.AlterModelOptions(
            name="exhibitionpage",
            options={
                "verbose_name": "exhibition page",
                "verbose_name_plural": "exhibition pages",
            },
        ),
        migrations.RemoveField(
            model_name="exhibitionpage",
            name="articles_title",
        ),
        migrations.RemoveField(
            model_name="exhibitionpage",
            name="dwell_time",
        ),
        migrations.RemoveField(
            model_name="exhibitionpage",
            name="hero_text_colour",
        ),
        migrations.RemoveField(
            model_name="exhibitionpage",
            name="location",
        ),
        migrations.RemoveField(
            model_name="exhibitionpage",
            name="location_url",
        ),
        migrations.RemoveField(
            model_name="exhibitionpage",
            name="max_price",
        ),
        migrations.RemoveField(
            model_name="exhibitionpage",
            name="min_price",
        ),
        migrations.RemoveField(
            model_name="exhibitionpage",
            name="need_to_know",
        ),
        migrations.RemoveField(
            model_name="exhibitionpage",
            name="need_to_know_cta",
        ),
        migrations.RemoveField(
            model_name="exhibitionpage",
            name="need_to_know_image",
        ),
        migrations.RemoveField(
            model_name="exhibitionpage",
            name="need_to_know_url",
        ),
        migrations.RemoveField(
            model_name="exhibitionpage",
            name="related_articles",
        ),
        migrations.RemoveField(
            model_name="exhibitionpage",
            name="short_title",
        ),
        migrations.RemoveField(
            model_name="exhibitionpage",
            name="target_audience",
        ),
        migrations.AddField(
            model_name="exhibitionpage",
            name="accent_colour",
            field=models.CharField(
                choices=[
                    ("none", "None"),
                    ("black", "Black"),
                    ("pink", "Pink"),
                    ("orange", "Orange"),
                    ("yellow", "Yellow"),
                    ("green", "Green"),
                    ("blue", "Blue"),
                ],
                default="none",
                help_text="The accent colour of the page where relevant.",
                max_length=20,
                verbose_name="page accent colour",
            ),
        ),
        migrations.AddField(
            model_name="exhibitionpage",
            name="audience_detail",
            field=models.CharField(
                blank=True,
                help_text="The text for the audience detail section.",
                max_length=40,
                verbose_name="audience detail",
            ),
        ),
        migrations.AddField(
            model_name="exhibitionpage",
            name="audience_heading",
            field=models.CharField(
                blank=True,
                help_text="The heading for the audience detail section.",
                max_length=40,
                verbose_name="audience heading",
            ),
        ),
        migrations.AddField(
            model_name="exhibitionpage",
            name="booking_details",
            field=wagtail.fields.RichTextField(
                help_text="Information about how to book tickets for the exhibition.",
                max_length=40,
                null=True,
                verbose_name="booking details",
            ),
        ),
        migrations.AddField(
            model_name="exhibitionpage",
            name="event_links",
            field=wagtail.fields.StreamField(
                [("event_links", 5)],
                block_lookup={
                    0: (
                        "wagtail.blocks.CharBlock",
                        (),
                        {"label": "Title", "max_length": 100},
                    ),
                    1: ("wagtail.blocks.CharBlock", (), {"label": "Description"}),
                    2: ("wagtail.blocks.URLBlock", (), {"label": "URL"}),
                    3: (
                        "etna.core.blocks.image.APIImageChooserBlock",
                        (),
                        {"label": "Image", "required": False},
                    ),
                    4: (
                        "wagtail.blocks.StructBlock",
                        [[("title", 0), ("description", 1), ("url", 2), ("image", 3)]],
                        {},
                    ),
                    5: ("wagtail.blocks.ListBlock", (4,), {"max_num": 2}),
                },
                null=True,
            ),
        ),
        migrations.AddField(
            model_name="exhibitionpage",
            name="event_title",
            field=models.CharField(
                default="Exhibition events",
                help_text="The title of the events section.",
                max_length=100,
                verbose_name="event title",
            ),
        ),
        migrations.AddField(
            model_name="exhibitionpage",
            name="exclude_days",
            field=models.BooleanField(
                default=False,
                help_text="Check this box to show only the month and year on the exhibition.",
                verbose_name="exclude days",
            ),
        ),
        migrations.AddField(
            model_name="exhibitionpage",
            name="exhibition_highlights",
            field=wagtail.fields.StreamField(
                [("exhibition_highlights", 7)],
                blank=True,
                block_lookup={
                    0: ("wagtail.blocks.CharBlock", (), {"required": False}),
                    1: (
                        "etna.core.blocks.paragraph.APIRichTextBlock",
                        (),
                        {"features": ["bold", "italic", "link"], "required": False},
                    ),
                    2: (
                        "etna.core.blocks.image.APIImageChooserBlock",
                        (),
                        {"rendition_size": "max-900x900", "required": True},
                    ),
                    3: (
                        "wagtail.blocks.CharBlock",
                        (),
                        {
                            "help_text": 'Alternative (alt) text describes images when they fail to load, and is read aloud by assistive technologies. Use a maximum of 100 characters to describe your image. <a href="https://html.spec.whatwg.org/multipage/images.html#alt" target="_blank">Check the guidance for tips on writing alt text</a>.',
                            "label": "Alternative text",
                            "max_length": 100,
                        },
                    ),
                    4: (
                        "etna.core.blocks.paragraph.APIRichTextBlock",
                        (),
                        {
                            "features": ["bold", "italic", "link"],
                            "help_text": "If provided, displays directly below the image. Can be used to specify sources, transcripts or other useful metadata.",
                            "label": "Caption (optional)",
                            "required": False,
                        },
                    ),
                    5: (
                        "wagtail.blocks.StructBlock",
                        [[("image", 2), ("alt_text", 3), ("caption", 4)]],
                        {},
                    ),
                    6: ("wagtail.blocks.ListBlock", (5,), {}),
                    7: (
                        "wagtail.blocks.StructBlock",
                        [[("title", 0), ("description", 1), ("images", 6)]],
                        {},
                    ),
                },
            ),
        ),
        migrations.AddField(
            model_name="exhibitionpage",
            name="featured_page",
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.SET_NULL,
                related_name="+",
                to="wagtailcore.page",
            ),
        ),
        migrations.AddField(
            model_name="exhibitionpage",
            name="hero_accent_colour",
            field=models.CharField(
                choices=[
                    ("none", "None"),
                    ("contrast", "Contrast"),
                    ("tint", "Tint"),
                    ("accent", "Accent"),
                ],
                default="none",
                help_text="The accent colour of the hero component.",
                max_length=20,
                verbose_name="hero component colour",
            ),
        ),
        migrations.AddField(
            model_name="exhibitionpage",
            name="hero_image_caption",
            field=wagtail.fields.RichTextField(
                blank=True,
                help_text="An optional caption for hero images. This could be used for image sources or for other useful metadata.",
                verbose_name="hero image caption (optional)",
            ),
        ),
        migrations.AddField(
            model_name="exhibitionpage",
            name="location_link_text",
            field=models.CharField(
                help_text="The text for the location section.",
                null=True,
                verbose_name="location link text",
            ),
        ),
        migrations.AddField(
            model_name="exhibitionpage",
            name="location_link_url",
            field=models.URLField(
                help_text="The URL for the location section.",
                max_length=255,
                null=True,
                verbose_name="location link URL",
            ),
        ),
        migrations.AddField(
            model_name="exhibitionpage",
            name="location_space_name",
            field=models.CharField(
                help_text="The location of the exhibition within the venue.",
                max_length=40,
                null=True,
                verbose_name="location space name",
            ),
        ),
        migrations.AddField(
            model_name="exhibitionpage",
            name="open_days",
            field=models.CharField(
                blank=True,
                help_text="The days the exhibition is open, e.g. Tuesday to Sunday.",
                max_length=255,
                verbose_name="open days",
            ),
        ),
        migrations.AddField(
            model_name="exhibitionpage",
            name="plan_your_visit",
            field=wagtail.fields.StreamField(
                [("plan_your_visit", 3)],
                blank=True,
                block_lookup={
                    0: ("wagtail.blocks.CharBlock", (), {"required": True}),
                    1: (
                        "etna.core.blocks.paragraph.APIRichTextBlock",
                        (),
                        {
                            "features": ["bold", "italic", "link", "ol", "ul"],
                            "required": True,
                        },
                    ),
                    2: (
                        "wagtail.blocks.StructBlock",
                        [[("title", 0), ("body", 1)]],
                        {},
                    ),
                    3: ("wagtail.blocks.ListBlock", (2,), {}),
                },
            ),
        ),
        migrations.AddField(
            model_name="exhibitionpage",
            name="price",
            field=models.FloatField(default=0, verbose_name="price"),
        ),
        migrations.AddField(
            model_name="exhibitionpage",
            name="related_pages",
            field=wagtail.fields.StreamField(
                [("featured_page", 2), ("featured_external_link", 7)],
                blank=True,
                block_lookup={
                    0: (
                        "etna.core.blocks.page_chooser.APIPageChooserBlock",
                        (),
                        {
                            "label": "Page",
                            "page_type": ["wagtailcore.Page"],
                            "required": True,
                        },
                    ),
                    1: (
                        "wagtail.blocks.CharBlock",
                        (),
                        {
                            "help_text": "Optional override for the teaser text",
                            "label": "Teaser text override",
                            "required": False,
                        },
                    ),
                    2: (
                        "wagtail.blocks.StructBlock",
                        [[("page", 0), ("teaser_text", 1)]],
                        {},
                    ),
                    3: (
                        "wagtail.blocks.CharBlock",
                        (),
                        {"label": "Title", "max_length": 100},
                    ),
                    4: ("wagtail.blocks.CharBlock", (), {"label": "Description"}),
                    5: ("wagtail.blocks.URLBlock", (), {"label": "URL"}),
                    6: (
                        "etna.core.blocks.image.APIImageChooserBlock",
                        (),
                        {"label": "Image", "required": False},
                    ),
                    7: (
                        "wagtail.blocks.StructBlock",
                        [[("title", 3), ("description", 4), ("url", 5), ("image", 6)]],
                        {},
                    ),
                },
                null=True,
            ),
        ),
        migrations.AddField(
            model_name="exhibitionpage",
            name="related_pages_title",
            field=models.CharField(
                blank=True,
                help_text="The title to display for the related content section.",
                max_length=255,
            ),
        ),
        migrations.AddField(
            model_name="exhibitionpage",
            name="review",
            field=wagtail.fields.StreamField(
                [("review", 3)],
                blank=True,
                block_lookup={
                    0: (
                        "etna.core.blocks.paragraph.APIRichTextBlock",
                        (),
                        {"features": ["bold", "italic", "link"], "required": True},
                    ),
                    1: (
                        "wagtail.blocks.CharBlock",
                        (),
                        {"max_length": 100, "required": False},
                    ),
                    2: (
                        "wagtail.blocks.ChoiceBlock",
                        [],
                        {
                            "choices": [
                                (0, "No stars"),
                                (3, "3 stars"),
                                (4, "4 stars"),
                                (5, "5 stars"),
                            ],
                            "icon": "pick",
                        },
                    ),
                    3: (
                        "wagtail.blocks.StructBlock",
                        [[("quote", 0), ("attribution", 1), ("stars", 2)]],
                        {},
                    ),
                },
            ),
        ),
        migrations.AddField(
            model_name="exhibitionpage",
            name="shop",
            field=wagtail.fields.StreamField(
                [("shop", 5)],
                blank=True,
                block_lookup={
                    0: (
                        "wagtail.blocks.CharBlock",
                        (),
                        {"label": "Title", "max_length": 100},
                    ),
                    1: (
                        "wagtail.blocks.CharBlock",
                        (),
                        {"label": "Description", "max_length": 255},
                    ),
                    2: (
                        "wagtail.blocks.CharBlock",
                        (),
                        {"default": "Shop now", "label": "CTA text", "max_length": 50},
                    ),
                    3: (
                        "wagtail.blocks.URLBlock",
                        (),
                        {"help_text": "The URL to the shop collection", "label": "URL"},
                    ),
                    4: (
                        "etna.core.blocks.image.APIImageChooserBlock",
                        (),
                        {"label": "Background image"},
                    ),
                    5: (
                        "wagtail.blocks.StructBlock",
                        [
                            [
                                ("title", 0),
                                ("description", 1),
                                ("cta_text", 2),
                                ("url", 3),
                                ("background_image", 4),
                            ]
                        ],
                        {},
                    ),
                },
            ),
        ),
        migrations.AddField(
            model_name="exhibitionpage",
            name="video",
            field=wagtail.fields.StreamField(
                [("youtube", 5), ("media", 9)],
                blank=True,
                block_lookup={
                    0: (
                        "wagtail.blocks.CharBlock",
                        (),
                        {"label": "Title", "max_length": 100, "required": True},
                    ),
                    1: (
                        "wagtail.blocks.CharBlock",
                        (),
                        {
                            "label": "YouTube Video ID",
                            "max_length": 11,
                            "required": True,
                            "validators": [
                                django.core.validators.RegexValidator(
                                    message="Invalid YouTube Video ID",
                                    regex="^[a-zA-Z0-9_-]{11}$",
                                )
                            ],
                        },
                    ),
                    2: (
                        "etna.core.blocks.image.APIImageChooserBlock",
                        (),
                        {
                            "label": "Preview Image",
                            "rendition_size": "max-640x360",
                            "required": False,
                        },
                    ),
                    3: (
                        "wagtail.blocks.RichTextBlock",
                        (),
                        {"label": "Transcript", "required": False},
                    ),
                    4: (
                        "wagtail.blocks.BooleanBlock",
                        (),
                        {
                            "help_text": "Tick if the video has captions on YouTube",
                            "label": "Captions available",
                            "required": False,
                        },
                    ),
                    5: (
                        "wagtail.blocks.StructBlock",
                        [
                            [
                                ("title", 0),
                                ("video_id", 1),
                                ("preview_image", 2),
                                ("transcript", 3),
                                ("captions_available", 4),
                            ]
                        ],
                        {},
                    ),
                    6: (
                        "wagtail.blocks.CharBlock",
                        (),
                        {
                            "help_text": "A descriptive title for the media block",
                            "required": True,
                        },
                    ),
                    7: (
                        "etna.core.blocks.image.APIImageChooserBlock",
                        (),
                        {
                            "help_text": "A thumbnail image for the media block",
                            "required": False,
                        },
                    ),
                    8: ("etna.media.blocks.MediaChooserBlock", (), {}),
                    9: (
                        "wagtail.blocks.StructBlock",
                        [[("title", 6), ("thumbnail", 7), ("media", 8)]],
                        {},
                    ),
                },
            ),
        ),
        migrations.AlterField(
            model_name="exhibitionpage",
            name="end_date",
            field=models.DateField(null=True, verbose_name="end date"),
        ),
        migrations.AlterField(
            model_name="exhibitionpage",
            name="hero_image",
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.SET_NULL,
                related_name="+",
                to="images.customimage",
            ),
        ),
        migrations.AlterField(
            model_name="exhibitionpage",
            name="start_date",
            field=models.DateField(null=True, verbose_name="start date"),
        ),
        migrations.AlterField(
            model_name="exhibitionpage",
            name="subtitle",
            field=models.CharField(
                help_text="A subtitle for the event.",
                max_length=120,
                verbose_name="subtitle",
            ),
        ),
        migrations.DeleteModel(
            name="ExhibitionHighlight",
        ),
    ]