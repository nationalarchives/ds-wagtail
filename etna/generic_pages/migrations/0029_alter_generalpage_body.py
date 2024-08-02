# Generated by Django 5.0.7 on 2024-08-01 15:32
# etna:allowAlterField

import etna.records.blocks
import wagtail.fields
from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ("generic_pages", "0028_generalpage_hero_image_and_more"),
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
                    ("description_list", 21),
                    ("document", 6),
                    ("do_dont_list", 26),
                    ("featured_record_article", 28),
                    ("image", 32),
                    ("image_gallery", 36),
                    ("inset_text", 38),
                    ("media", 42),
                    ("paragraph", 38),
                    ("promoted_item", 54),
                    ("promoted_list", 61),
                    ("quote", 64),
                    ("record_links", 66),
                    ("table", 68),
                    ("warning_text", 69),
                    ("youtube_video", 73),
                    ("content_section", 80),
                ],
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
                        "etna.core.blocks.page_chooser.APIPageChooserBlock",
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
                        "etna.core.blocks.paragraph.APIRichTextBlock",
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
                        "etna.core.blocks.paragraph.APIRichTextBlock",
                        (),
                        {"features": ["bold", "italic", "link"]},
                    ),
                    19: (
                        "wagtail.blocks.StructBlock",
                        [[("term", 0), ("detail", 18)]],
                        {},
                    ),
                    20: ("wagtail.blocks.ListBlock", (19,), {}),
                    21: ("wagtail.blocks.StructBlock", [[("items", 20)]], {}),
                    22: (
                        "wagtail.blocks.StructBlock",
                        [[("text", 18)]],
                        {"icon": "check", "label": "Do item"},
                    ),
                    23: ("wagtail.blocks.ListBlock", (22,), {"label": "Dos"}),
                    24: (
                        "wagtail.blocks.StructBlock",
                        [[("text", 18)]],
                        {"icon": "cross", "label": "Don't item"},
                    ),
                    25: ("wagtail.blocks.ListBlock", (24,), {"label": "Don'ts"}),
                    26: (
                        "wagtail.blocks.StructBlock",
                        [[("do", 23), ("dont", 25)]],
                        {},
                    ),
                    27: (
                        "etna.core.blocks.page_chooser.APIPageChooserBlock",
                        (),
                        {
                            "label": "Page",
                            "page_type": ["articles.RecordArticlePage"],
                            "required_api_fields": ["teaser_image"],
                        },
                    ),
                    28: ("wagtail.blocks.StructBlock", [[("page", 27)]], {}),
                    29: (
                        "etna.core.blocks.image.APIImageChooserBlock",
                        (),
                        {"rendition_size": "max-900x900", "required": True},
                    ),
                    30: (
                        "wagtail.blocks.CharBlock",
                        (),
                        {
                            "help_text": 'Alternative (alt) text describes images when they fail to load, and is read aloud by assistive technologies. Use a maximum of 100 characters to describe your image. <a href="https://html.spec.whatwg.org/multipage/images.html#alt" target="_blank">Check the guidance for tips on writing alt text</a>.',
                            "label": "Alternative text",
                            "max_length": 100,
                        },
                    ),
                    31: (
                        "etna.core.blocks.paragraph.APIRichTextBlock",
                        (),
                        {
                            "features": ["bold", "italic", "link"],
                            "help_text": "If provided, displays directly below the image. Can be used to specify sources, transcripts or other useful metadata.",
                            "label": "Caption (optional)",
                            "required": False,
                        },
                    ),
                    32: (
                        "wagtail.blocks.StructBlock",
                        [[("image", 29), ("alt_text", 30), ("caption", 31)]],
                        {},
                    ),
                    33: ("wagtail.blocks.CharBlock", (), {"required": False}),
                    34: (
                        "etna.core.blocks.paragraph.APIRichTextBlock",
                        (),
                        {"features": ["bold", "italic", "link"], "required": False},
                    ),
                    35: ("wagtail.blocks.ListBlock", (32,), {}),
                    36: (
                        "wagtail.blocks.StructBlock",
                        [[("title", 33), ("description", 34), ("images", 35)]],
                        {},
                    ),
                    37: (
                        "etna.core.blocks.paragraph.APIRichTextBlock",
                        (),
                        {"features": ["bold", "italic", "link", "ol", "ul"]},
                    ),
                    38: ("wagtail.blocks.StructBlock", [[("text", 37)]], {}),
                    39: (
                        "wagtail.blocks.CharBlock",
                        (),
                        {
                            "help_text": "A descriptive title for the media block",
                            "required": True,
                        },
                    ),
                    40: (
                        "etna.core.blocks.image.APIImageChooserBlock",
                        (),
                        {"help_text": "A background image for the media block"},
                    ),
                    41: ("etna.media.blocks.MediaChooserBlock", (), {}),
                    42: (
                        "wagtail.blocks.StructBlock",
                        [[("title", 39), ("background_image", 40), ("media", 41)]],
                        {},
                    ),
                    43: (
                        "wagtail.blocks.CharBlock",
                        (),
                        {
                            "help_text": "Title of the promoted page",
                            "label": "Title",
                            "max_length": 100,
                        },
                    ),
                    44: (
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
                    45: (
                        "wagtail.blocks.CharBlock",
                        (),
                        {
                            "help_text": "This is a free text field. Please enter date as per agreed format: 14 April 2021",
                            "required": False,
                        },
                    ),
                    46: (
                        "wagtail.blocks.CharBlock",
                        (),
                        {
                            "help_text": "Podcast or video duration.",
                            "label": "Duration",
                            "max_length": 50,
                            "required": False,
                        },
                    ),
                    47: (
                        "wagtail.blocks.URLBlock",
                        (),
                        {
                            "help_text": "URL for the external page",
                            "label": "External URL",
                        },
                    ),
                    48: (
                        "wagtail.blocks.BooleanBlock",
                        (),
                        {
                            "label": "Should this URL open in a new tab? <p style='font-size: 11px;'>Tick the box if 'yes'</p>",
                            "required": False,
                        },
                    ),
                    49: (
                        "wagtail.blocks.CharBlock",
                        (),
                        {
                            "help_text": "The text displayed on the button for your URL. If your URL links to an external site, please add the name of the site users will land on, and what they will find on this page. For example 'Watch our short film  <strong>about Shakespeare on YouTube</strong>'.",
                            "label": "Call to action label",
                            "max_length": 50,
                        },
                    ),
                    50: (
                        "wagtail.blocks.BooleanBlock",
                        (),
                        {
                            "default": False,
                            "help_text": 'Decorative images are used for visual effect and do not add information to the content of a page. <a href="https://www.w3.org/WAI/tutorials/images/decorative/" target="_blank">"Check the guidance to see if your image is decorative</a>.',
                            "label": "Is this image decorative? <p class='field-title__subheading'>Tick the box if 'yes'</p>",
                            "required": False,
                        },
                    ),
                    51: (
                        "wagtail.blocks.CharBlock",
                        (),
                        {
                            "help_text": 'Alternative (alt) text describes images when they fail to load, and is read aloud by assistive technologies. Use a maximum of 100 characters to describe your image. Decorative images do not require alt text. <a href="https://html.spec.whatwg.org/multipage/images.html#alt" target="_blank">Check the guidance for tips on writing alt text</a>.',
                            "label": "Image alternative text",
                            "max_length": 100,
                            "required": False,
                        },
                    ),
                    52: (
                        "wagtail.blocks.StructBlock",
                        [[("image", 29), ("decorative", 50), ("alt_text", 51)]],
                        {
                            "label": "Teaser image",
                            "template": "articles/blocks/images/blog-embed__image-container.html",
                        },
                    ),
                    53: (
                        "etna.core.blocks.paragraph.APIRichTextBlock",
                        (),
                        {
                            "features": ["bold", "italic", "link"],
                            "help_text": "A description of the promoted page",
                        },
                    ),
                    54: (
                        "wagtail.blocks.StructBlock",
                        [
                            [
                                ("title", 43),
                                ("category", 44),
                                ("publication_date", 45),
                                ("author", 33),
                                ("duration", 46),
                                ("url", 47),
                                ("target_blank", 48),
                                ("cta_label", 49),
                                ("image", 52),
                                ("description", 53),
                            ]
                        ],
                        {},
                    ),
                    55: (
                        "wagtail.snippets.blocks.SnippetChooserBlock",
                        ("categories.Category",),
                        {},
                    ),
                    56: (
                        "wagtail.blocks.CharBlock",
                        (),
                        {
                            "help_text": "The title of the target page",
                            "max_length": 100,
                            "required": True,
                        },
                    ),
                    57: (
                        "etna.core.blocks.paragraph.APIRichTextBlock",
                        (),
                        {
                            "features": ["bold", "italic", "link"],
                            "help_text": "A description of the target page",
                            "required": False,
                        },
                    ),
                    58: ("wagtail.blocks.URLBlock", (), {"required": True}),
                    59: (
                        "wagtail.blocks.StructBlock",
                        [[("title", 56), ("description", 57), ("url", 58)]],
                        {},
                    ),
                    60: ("wagtail.blocks.ListBlock", (59,), {}),
                    61: (
                        "wagtail.blocks.StructBlock",
                        [[("category", 55), ("summary", 34), ("promoted_items", 60)]],
                        {},
                    ),
                    62: (
                        "etna.core.blocks.paragraph.APIRichTextBlock",
                        (),
                        {"features": ["bold", "italic", "link"], "required": True},
                    ),
                    63: (
                        "wagtail.blocks.CharBlock",
                        (),
                        {"max_length": 100, "required": False},
                    ),
                    64: (
                        "wagtail.blocks.StructBlock",
                        [[("quote", 62), ("attribution", 63)]],
                        {},
                    ),
                    65: (
                        "wagtail.blocks.ListBlock",
                        (etna.records.blocks.RecordLinkBlock,),
                        {"label": "Items"},
                    ),
                    66: ("wagtail.blocks.StructBlock", [[("items", 65)]], {}),
                    67: (
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
                    68: ("wagtail.blocks.StructBlock", [[("table", 67)]], {}),
                    69: ("wagtail.blocks.StructBlock", [[("body", 37)]], {}),
                    70: (
                        "wagtail.blocks.CharBlock",
                        (),
                        {"label": "Title", "max_length": 100, "required": True},
                    ),
                    71: (
                        "wagtail.blocks.CharBlock",
                        (),
                        {
                            "label": "YouTube Video ID",
                            "max_length": 11,
                            "required": True,
                        },
                    ),
                    72: (
                        "etna.core.blocks.image.APIImageChooserBlock",
                        (),
                        {
                            "label": "Preview Image",
                            "rendition_size": "max-640x360",
                            "required": False,
                        },
                    ),
                    73: (
                        "wagtail.blocks.StructBlock",
                        [[("title", 70), ("video_id", 71), ("preview_image", 72)]],
                        {},
                    ),
                    74: (
                        "wagtail.blocks.CharBlock",
                        (),
                        {"label": "Heading", "max_length": 100},
                    ),
                    75: (
                        "wagtail.blocks.CharBlock",
                        (),
                        {"label": "Sub-heading", "max_length": 100},
                    ),
                    76: ("wagtail.blocks.StructBlock", [[("heading", 75)]], {}),
                    77: (
                        "wagtail.blocks.CharBlock",
                        (),
                        {"label": "Sub-sub-heading", "max_length": 100},
                    ),
                    78: ("wagtail.blocks.StructBlock", [[("heading", 77)]], {}),
                    79: (
                        "wagtail.blocks.StreamBlock",
                        [
                            [
                                ("accordions", 10),
                                ("button", 15),
                                ("call_to_action", 17),
                                ("description_list", 21),
                                ("document", 6),
                                ("do_dont_list", 26),
                                ("featured_record_article", 28),
                                ("image", 32),
                                ("image_gallery", 36),
                                ("inset_text", 38),
                                ("media", 42),
                                ("paragraph", 38),
                                ("promoted_item", 54),
                                ("promoted_list", 61),
                                ("quote", 64),
                                ("record_links", 66),
                                ("sub_heading", 76),
                                ("sub_sub_heading", 78),
                                ("table", 68),
                                ("warning_text", 69),
                                ("youtube_video", 73),
                            ]
                        ],
                        {"required": False},
                    ),
                    80: (
                        "wagtail.blocks.StructBlock",
                        [[("heading", 74), ("content", 79)]],
                        {},
                    ),
                },
                null=True,
            ),
        ),
    ]