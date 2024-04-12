from wagtail import blocks

from etna.core.blocks.image import APIImageChooserBlock


class PromotedLinkBlock(blocks.StructBlock):
    url = blocks.URLBlock(label="External URL", help_text="URL for the external page")
    title = blocks.CharBlock(max_length=100, help_text="Title of the promoted page")
    teaser_image = APIImageChooserBlock(
        help_text="Image that will appear on thumbnails and promos around the site."
    )
    description = blocks.CharBlock(
        max_length=200, help_text="A description of the promoted page"
    )
