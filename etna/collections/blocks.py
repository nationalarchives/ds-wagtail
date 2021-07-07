from wagtail.core import blocks

from ..quotes.blocks import QuoteBlock


class ExplorerPageStreamBlock(blocks.StreamBlock):
    quote = QuoteBlock()


class CategoryPageStreamBlock(blocks.StreamBlock):
    quote = QuoteBlock()
