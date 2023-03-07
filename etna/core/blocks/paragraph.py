from django.conf import settings

from wagtail import blocks


class ParagraphBlock(blocks.StructBlock):
    text = blocks.RichTextBlock(features=settings.RESTRICTED_RICH_TEXT_FEATURES)

    class Meta:
        icon = "paragraph"
        label = "Paragraph text"
        template = "blocks/paragraph.html"


class ParagraphWithHeading(blocks.StructBlock):
    """
    Paragraph with heading streamfield component.
    """

    heading = blocks.CharBlock(required=True, max_length=100)
    paragraph = blocks.RichTextBlock(
        required=True, features=settings.RESTRICTED_RICH_TEXT_FEATURES
    )

    class Meta:
        icon = "paragraph"
        label = "Paragraph with heading"
        template = "blocks/paragraph-with-heading.html"
