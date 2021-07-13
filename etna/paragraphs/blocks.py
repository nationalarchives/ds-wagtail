from django.conf import settings

from wagtail.core import blocks


class ParagraphWithHeading(blocks.StructBlock):
    """
    Paragraph with heading streamfield component.
    """
    heading = blocks.CharBlock(required=True, max_length=100)
    paragraph = blocks.RichTextBlock(required=True, features=settings.INLINE_RICH_TEXT_FEATURES)

    class Meta:
        icon = 'fa-paragraph'
        label = 'Paragraph with heading'
        template = 'paragraphs/blocks/paragraph-with-heading.html'
