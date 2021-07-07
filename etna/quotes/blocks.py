from wagtail.core import blocks

from ..richtexts.blocks import BasicRichTextBlock


class QuoteBlock(blocks.StructBlock):
    """
    Quote streamfield component
    """
    title = blocks.CharBlock(required=True, max_length=100)
    quote = BasicRichTextBlock(required=True)
    attribution = blocks.CharBlock(required=False, max_length=100)


    class Meta:
        icon = 'openquote'
        label = 'Quote'
        template = 'quotes/blocks/quote.html'
