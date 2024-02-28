from etna.core.blocks import ParagraphBlock
from wagtail import blocks


class GeneralPageStreamBlock(blocks.StreamBlock):
    paragraph = ParagraphBlock()
