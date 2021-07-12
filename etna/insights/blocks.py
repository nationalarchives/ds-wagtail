from wagtail.core import blocks

from ..quotes.blocks import QuoteBlock

class InsightsPageStreamBlock(blocks.StreamBlock):
    quote = QuoteBlock()
