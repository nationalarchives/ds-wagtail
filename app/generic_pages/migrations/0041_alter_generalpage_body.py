# Generated by Django 5.1.4 on 2025-01-07 11:44
# etna:allowAlterField

import django.core.validators
import app.ciim.blocks
import wagtail.fields
from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ("generic_pages", "0040_alter_generalpage_body"),
    ]

    operations = [
        migrations.AlterField(
            model_name="generalpage",
            name="body",
            field=wagtail.fields.StreamField(
                [
                    ("accordions", 10),
                    ("button", 15),
                    ("call_to_action", 17),
                    ("contact", 23),
                    ("description_list", 27),
                    ("details", 28),
                    ("document", 6),
                    ("do_dont_list", 33),
                    ("featured_external_link", 38),
                    ("featured_page", 41),
                    ("featured_record_article", 43),
                    ("image", 47),
                    ("image_gallery", 49),
                    ("inset_text", 51),
                    ("media", 55),
                    ("paragraph", 51),
                    ("promoted_item", 67),
                    ("quote", 69),
                    ("record_links", 71),
                    ("table", 73),
                    ("warning_text", 74),
                    ("youtube_video", 80),
                    ("content_section", 87),
                ],
                blank=True,
                block_lookup={
                    0: ("wagtail.blocks.CharBlock", (), {"required": True}),
                    1: (
                        "app.core.blocks.paragraph.APIRichTextBlock",
                        (),
                        {
                            "features": ["bold", "italic", "link", "ol", "ul"],
                            "required": True,
                        },
                    ),
                    2: ("wagtail.contrib.table_block.blocks.TableBlock", (), {}),
                    3: (
                        "wagtail.documents.blocks.DocumentChooserBlock",
                        (),
                        {"required": True},
                    ),
                    4: ("wagtail.blocks.StructBlock", [[("file", 3)]], {}),
                    5: ("wagtail.blocks.ListBlock", (4,), {}),
                    6: ("wagtail.blocks.StructBlock", [[("documents", 5)]], {}),
                    7: (
                        "wagtail.blocks.StreamBlock",
                        [[("text", 1), ("table", 2), ("documents", 6)]],
                        {},
                    ),
                    8: (
                        "wagtail.blocks.StructBlock",
                        [[("title", 0), ("body", 7)]],
                        {},
                    ),
                    9: ("wagtail.blocks.ListBlock", (8,), {}),
                    10: ("wagtail.blocks.StructBlock", [[("items", 9)]], {}),
                    11: ("wagtail.blocks.CharBlock", (), {}),
                    12: (
                        "app.core.blocks.page_chooser.APIPageChooserBlock",
                        (),
                        {"required": False},
                    ),
                    13: ("wagtail.blocks.URLBlock", (), {"required": False}),
                    14: (
                        "wagtail.blocks.BooleanBlock",
                        (),
                        {
                            "help_text": "Use the accented button style",
                            "label": "Accented",
                            "required": False,
                        },
                    ),
                    15: (
                        "wagtail.blocks.StructBlock",
                        [
                            [
                                ("label", 11),
                                ("link", 12),
                                ("external_link", 13),
                                ("accented", 14),
                            ]
                        ],
                        {},
                    ),
                    16: (
                        "app.core.blocks.paragraph.APIRichTextBlock",
                        (),
                        {
                            "features": ["bold", "italic", "link", "ol", "ul"],
                            "max_length": 100,
                        },
                    ),
                    17: (
                        "wagtail.blocks.StructBlock",
                        [[("body", 16), ("button", 15)]],
                        {},
                    ),
                    18: (
                        "wagtail.blocks.TextBlock",
                        (),
                        {"features": ["bold", "italic", "link"], "required": False},
                    ),
                    19: ("wagtail.blocks.CharBlock", (), {"required": False}),
                    20: (
                        "app.core.blocks.paragraph.APIRichTextBlock",
                        (),
                        {"required": False},
                    ),
                    21: ("wagtail.blocks.EmailBlock", (), {"required": False}),
                    22: (
                        "app.core.blocks.paragraph.APIRichTextBlock",
                        (),
                        {"features": ["bold", "italic", "link"], "required": False},
                    ),
                    23: (
                        "wagtail.blocks.StructBlock",
                        [
                            [
                                ("title", 11),
                                ("address", 18),
                                ("telephone", 19),
                                ("chat_link", 13),
                                ("chat_note", 20),
                                ("email", 21),
                                ("website_link", 13),
                                ("social_media", 22),
                            ]
                        ],
                        {},
                    ),
                    24: (
                        "app.core.blocks.paragraph.APIRichTextBlock",
                        (),
                        {"features": ["bold", "italic", "link"]},
                    ),
                    25: (
                        "wagtail.blocks.StructBlock",
                        [[("term", 0), ("detail", 24)]],
                        {},
                    ),
                    26: ("wagtail.blocks.ListBlock", (25,), {}),
                    27: ("wagtail.blocks.StructBlock", [[("items", 26)]], {}),
                    28: (
                        "wagtail.blocks.StructBlock",
                        [[("title", 0), ("body", 1)]],
                        {},
                    ),
                    29: (
                        "wagtail.blocks.StructBlock",
                        [[("text", 24)]],
                        {"icon": "check", "label": "Do item"},
                    ),
                    30: ("wagtail.blocks.ListBlock", (29,), {"label": "Dos"}),
                    31: (
                        "wagtail.blocks.StructBlock",
                        [[("text", 24)]],
                        {"icon": "cross", "label": "Don't item"},
                    ),
                    32: ("wagtail.blocks.ListBlock", (31,), {"label": "Don'ts"}),
                    33: (
                        "wagtail.blocks.StructBlock",
                        [[("do", 30), ("dont", 32)]],
                        {},
                    ),
                    34: (
                        "wagtail.blocks.CharBlock",
                        (),
                        {"label": "Title", "max_length": 100},
                    ),
                    35: ("wagtail.blocks.CharBlock", (), {"label": "Description"}),
                    36: ("wagtail.blocks.URLBlock", (), {"label": "URL"}),
                    37: (
                        "app.core.blocks.image.APIImageChooserBlock",
                        (),
                        {"label": "Image", "required": False},
                    ),
                    38: (
                        "wagtail.blocks.StructBlock",
                        [
                            [
                                ("title", 34),
                                ("description", 35),
                                ("url", 36),
                                ("image", 37),
                            ]
                        ],
                        {},
                    ),
                    39: (
                        "app.core.blocks.page_chooser.APIPageChooserBlock",
                        (),
                        {
                            "label": "Page",
                            "page_type": ["wagtailcore.Page"],
                            "required": True,
                        },
                    ),
                    40: (
                        "wagtail.blocks.CharBlock",
                        (),
                        {
                            "help_text": "Optional override for the teaser text",
                            "label": "Teaser text override",
                            "required": False,
                        },
                    ),
                    41: (
                        "wagtail.blocks.StructBlock",
                        [[("page", 39), ("teaser_text", 40)]],
                        {},
                    ),
                    42: (
                        "app.core.blocks.page_chooser.APIPageChooserBlock",
                        (),
                        {
                            "label": "Page",
                            "page_type": ["articles.RecordArticlePage"],
                            "required_api_fields": ["teaser_image"],
                        },
                    ),
                    43: ("wagtail.blocks.StructBlock", [[("page", 42)]], {}),
                    44: (
                        "app.core.blocks.image.APIImageChooserBlock",
                        (),
                        {"rendition_size": "max-900x900", "required": True},
                    ),
                    45: (
                        "wagtail.blocks.CharBlock",
                        (),
                        {
                            "help_text": 'Alternative (alt) text describes images when they fail to load, and is read aloud by assistive technologies. Use a maximum of 100 characters to describe your image. <a href="https://html.spec.whatwg.org/multipage/images.html#alt" target="_blank">Check the guidance for tips on writing alt text</a>.',
                            "label": "Alternative text",
                            "max_length": 100,
                        },
                    ),
                    46: (
                        "app.core.blocks.paragraph.APIRichTextBlock",
                        (),
                        {
                            "features": ["bold", "italic", "link"],
                            "help_text": "If provided, displays directly below the image. Can be used to specify sources, transcripts or other useful metadata.",
                            "label": "Caption (optional)",
                            "required": False,
                        },
                    ),
                    47: (
                        "wagtail.blocks.StructBlock",
                        [[("image", 44), ("alt_text", 45), ("caption", 46)]],
                        {},
                    ),
                    48: ("wagtail.blocks.ListBlock", (47,), {}),
                    49: (
                        "wagtail.blocks.StructBlock",
                        [[("title", 19), ("description", 22), ("images", 48)]],
                        {},
                    ),
                    50: (
                        "app.core.blocks.paragraph.APIRichTextBlock",
                        (),
                        {"features": ["bold", "italic", "link", "ol", "ul"]},
                    ),
                    51: ("wagtail.blocks.StructBlock", [[("text", 50)]], {}),
                    52: (
                        "wagtail.blocks.CharBlock",
                        (),
                        {
                            "help_text": "A descriptive title for the media block",
                            "required": True,
                        },
                    ),
                    53: (
                        "app.core.blocks.image.APIImageChooserBlock",
                        (),
                        {
                            "help_text": "A thumbnail image for the media block",
                            "required": False,
                        },
                    ),
                    54: ("app.media.blocks.MediaChooserBlock", (), {}),
                    55: (
                        "wagtail.blocks.StructBlock",
                        [[("title", 52), ("thumbnail", 53), ("media", 54)]],
                        {},
                    ),
                    56: (
                        "wagtail.blocks.CharBlock",
                        (),
                        {
                            "help_text": "Title of the promoted page",
                            "label": "Title",
                            "max_length": 100,
                        },
                    ),
                    57: (
                        "wagtail.blocks.ChoiceBlock",
                        [],
                        {
                            "choices": [
                                ("blog", "Blog post"),
                                ("podcast", "Podcast"),
                                ("video", "Video"),
                                ("video-external", "External video"),
                                ("external-link", "External link"),
                            ],
                            "label": "Category",
                        },
                    ),
                    58: (
                        "wagtail.blocks.CharBlock",
                        (),
                        {
                            "help_text": "This is a free text field. Please enter date as per agreed format: 14 April 2021",
                            "required": False,
                        },
                    ),
                    59: (
                        "wagtail.blocks.CharBlock",
                        (),
                        {
                            "help_text": "Podcast or video duration.",
                            "label": "Duration",
                            "max_length": 50,
                            "required": False,
                        },
                    ),
                    60: (
                        "wagtail.blocks.URLBlock",
                        (),
                        {
                            "help_text": "URL for the external page",
                            "label": "External URL",
                        },
                    ),
                    61: (
                        "wagtail.blocks.BooleanBlock",
                        (),
                        {
                            "label": "Should this URL open in a new tab? <p style='font-size: 11px;'>Tick the box if 'yes'</p>",
                            "required": False,
                        },
                    ),
                    62: (
                        "wagtail.blocks.CharBlock",
                        (),
                        {
                            "help_text": "The text displayed on the button for your URL. If your URL links to an external site, please add the name of the site users will land on, and what they will find on this page. For example 'Watch our short film  <strong>about Shakespeare on YouTube</strong>'.",
                            "label": "Call to action label",
                            "max_length": 50,
                        },
                    ),
                    63: (
                        "wagtail.blocks.BooleanBlock",
                        (),
                        {
                            "default": False,
                            "help_text": 'Decorative images are used for visual effect and do not add information to the content of a page. <a href="https://www.w3.org/WAI/tutorials/images/decorative/" target="_blank">"Check the guidance to see if your image is decorative</a>.',
                            "label": "Is this image decorative? <p class='field-title__subheading'>Tick the box if 'yes'</p>",
                            "required": False,
                        },
                    ),
                    64: (
                        "wagtail.blocks.CharBlock",
                        (),
                        {
                            "help_text": 'Alternative (alt) text describes images when they fail to load, and is read aloud by assistive technologies. Use a maximum of 100 characters to describe your image. Decorative images do not require alt text. <a href="https://html.spec.whatwg.org/multipage/images.html#alt" target="_blank">Check the guidance for tips on writing alt text</a>.',
                            "label": "Image alternative text",
                            "max_length": 100,
                            "required": False,
                        },
                    ),
                    65: (
                        "wagtail.blocks.StructBlock",
                        [[("image", 44), ("decorative", 63), ("alt_text", 64)]],
                        {
                            "label": "Teaser image",
                            "template": "articles/blocks/images/blog-embed__image-container.html",
                        },
                    ),
                    66: (
                        "app.core.blocks.paragraph.APIRichTextBlock",
                        (),
                        {
                            "features": ["bold", "italic", "link"],
                            "help_text": "A description of the promoted page",
                        },
                    ),
                    67: (
                        "wagtail.blocks.StructBlock",
                        [
                            [
                                ("title", 56),
                                ("category", 57),
                                ("publication_date", 58),
                                ("author", 19),
                                ("duration", 59),
                                ("url", 60),
                                ("target_blank", 61),
                                ("cta_label", 62),
                                ("image", 65),
                                ("description", 66),
                            ]
                        ],
                        {},
                    ),
                    68: (
                        "wagtail.blocks.CharBlock",
                        (),
                        {"max_length": 100, "required": False},
                    ),
                    69: (
                        "wagtail.blocks.StructBlock",
                        [[("quote", 1), ("attribution", 68)]],
                        {},
                    ),
                    70: (
                        "wagtail.blocks.ListBlock",
                        (app.ciim.blocks.RecordLinkBlock,),
                        {"label": "Items"},
                    ),
                    71: ("wagtail.blocks.StructBlock", [[("items", 70)]], {}),
                    72: (
                        "wagtail.contrib.table_block.blocks.TableBlock",
                        (),
                        {
                            "table_options": {
                                "contextMenu": [
                                    "row_above",
                                    "row_below",
                                    "---------",
                                    "col_left",
                                    "col_right",
                                    "---------",
                                    "remove_row",
                                    "remove_col",
                                    "---------",
                                    "undo",
                                    "redo",
                                    "---------",
                                    "alignment",
                                ]
                            }
                        },
                    ),
                    73: ("wagtail.blocks.StructBlock", [[("table", 72)]], {}),
                    74: ("wagtail.blocks.StructBlock", [[("body", 50)]], {}),
                    75: (
                        "wagtail.blocks.CharBlock",
                        (),
                        {"label": "Title", "max_length": 100, "required": True},
                    ),
                    76: (
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
                    77: (
                        "app.core.blocks.image.APIImageChooserBlock",
                        (),
                        {
                            "label": "Preview Image",
                            "rendition_size": "fill-640x360",
                            "required": True,
                        },
                    ),
                    78: (
                        "wagtail.blocks.RichTextBlock",
                        (),
                        {"label": "Transcript", "required": False},
                    ),
                    79: (
                        "wagtail.blocks.BooleanBlock",
                        (),
                        {
                            "help_text": "Tick if the video has captions on YouTube",
                            "label": "Captions available",
                            "required": False,
                        },
                    ),
                    80: (
                        "wagtail.blocks.StructBlock",
                        [
                            [
                                ("title", 75),
                                ("video_id", 76),
                                ("preview_image", 77),
                                ("transcript", 78),
                                ("captions_available", 79),
                            ]
                        ],
                        {},
                    ),
                    81: (
                        "wagtail.blocks.CharBlock",
                        (),
                        {"label": "Heading", "max_length": 100},
                    ),
                    82: (
                        "wagtail.blocks.CharBlock",
                        (),
                        {"label": "Sub-heading", "max_length": 100},
                    ),
                    83: ("wagtail.blocks.StructBlock", [[("heading", 82)]], {}),
                    84: (
                        "wagtail.blocks.CharBlock",
                        (),
                        {"label": "Sub-sub-heading", "max_length": 100},
                    ),
                    85: ("wagtail.blocks.StructBlock", [[("heading", 84)]], {}),
                    86: (
                        "wagtail.blocks.StreamBlock",
                        [
                            [
                                ("accordions", 10),
                                ("button", 15),
                                ("call_to_action", 17),
                                ("contact", 23),
                                ("description_list", 27),
                                ("details", 28),
                                ("document", 6),
                                ("do_dont_list", 33),
                                ("featured_external_link", 38),
                                ("featured_page", 41),
                                ("featured_record_article", 43),
                                ("image", 47),
                                ("image_gallery", 49),
                                ("inset_text", 51),
                                ("media", 55),
                                ("paragraph", 51),
                                ("promoted_item", 67),
                                ("quote", 69),
                                ("record_links", 71),
                                ("sub_heading", 83),
                                ("sub_sub_heading", 85),
                                ("table", 73),
                                ("warning_text", 74),
                                ("youtube_video", 80),
                            ]
                        ],
                        {"required": False},
                    ),
                    87: (
                        "wagtail.blocks.StructBlock",
                        [[("heading", 81), ("content", 86)]],
                        {},
                    ),
                },
                null=True,
            ),
        ),
    ]
