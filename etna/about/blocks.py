from wagtail.core import blocks
from wagtail.images.blocks import ImageChooserBlock

from etna.core.blocks import ParagraphBlock, ParagraphWithHeading


class AboutPageStreamBlock(blocks.StreamBlock):
    paragraph = ParagraphBlock()
