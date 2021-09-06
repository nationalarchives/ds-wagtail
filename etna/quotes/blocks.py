from django.conf import settings

from wagtail.core import blocks


class QuoteBlock(blocks.StructBlock):
    """
    Quote streamfield component
    """
    heading = blocks.CharBlock(required=False, max_length=100)
    quote = blocks.RichTextBlock(required=True, features=settings.INLINE_RICH_TEXT_FEATURES)
    attribution = blocks.CharBlock(required=False, max_length=100)


    class Meta:
        icon = 'openquote'
        label = 'Quote'
        template = 'quotes/blocks/quote.html'
