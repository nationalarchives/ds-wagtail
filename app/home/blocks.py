from wagtail import blocks

from app.core.blocks import APIPageChooserBlock, ParagraphBlock
from app.core.blocks.image import APIImageChooserBlock
from app.core.blocks import FeaturedPageBlock, FeaturedExternalLinkBlock


class FeaturedItemBlock(blocks.StructBlock):
    featured_page = FeaturedPageBlock()
    featured_external_page = FeaturedExternalLinkBlock()

    class Meta:
        icon = "arrow-up"
