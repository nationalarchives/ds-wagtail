from wagtail.core import blocks

from etna.core.blocks import ParagraphBlock


class AboutPageStreamBlock(blocks.StreamBlock):
    paragraph = ParagraphBlock()
