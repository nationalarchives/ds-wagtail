from django.conf import settings

from wagtail.core import blocks


class ParagraphWithTitle(blocks.StructBlock):
    """
    Paragraph streamfield component.
    """
    title = blocks.CharBlock(required=True, max_length=100)
    paragraph = blocks.RichTextBlock(required=True, features=settings.INLINE_RICH_TEXT_FEATURES)

    class Meta:
        icon = 'fa-paragraph'
        label = 'Paragraph'
        template = 'paragraphs/blocks/paragraph-with-title.html'
