from django.conf import settings

from wagtail import blocks

from etna.core.blocks.paragraph import APIRichTextBlock


class QuoteBlock(blocks.StructBlock):
    """
    Quote streamfield component
    """

    quote = APIRichTextBlock(required=True, features=settings.INLINE_RICH_TEXT_FEATURES)
    attribution = blocks.CharBlock(required=False, max_length=100)

    class Meta:
        icon = "openquote"
        label = "Quote"
        template = "blocks/quote.html"
