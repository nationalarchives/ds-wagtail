from wagtail.core import blocks

from ..quotes.blocks import QuoteBlock
from ..paragraphs.blocks import ParagraphWithHeading
from ..links.blocks import LinkListBlock


class InsightsPageStreamBlock(blocks.StreamBlock):
    quote = QuoteBlock()
    paragraph_with_heading = ParagraphWithHeading()
    link_list = LinkListBlock()
