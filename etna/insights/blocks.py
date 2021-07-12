from wagtail.core import blocks

from ..quotes.blocks import QuoteBlock
from..paragraphs.blocks import ParagraphWithTitleAndImage


class InsightsPageStreamBlock(blocks.StreamBlock):
    quote = QuoteBlock()
    paragraph = ParagraphWithTitleAndImage()
