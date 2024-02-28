from wagtail import blocks

from etna.core.blocks import ParagraphBlock


class GeneralPageStreamBlock(blocks.StreamBlock):
    paragraph = ParagraphBlock()
