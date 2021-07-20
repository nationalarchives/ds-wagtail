from wagtail.core import blocks

from ..quotes.blocks import QuoteBlock
from ..paragraphs.blocks import ParagraphWithHeading
from ..sections.blocks import SectionHeadingBlock


class InsightsPageStreamBlock(blocks.StreamBlock):
    quote = QuoteBlock()
    paragraph_with_heading = ParagraphWithHeading()
    section_heading = SectionHeadingBlock()
