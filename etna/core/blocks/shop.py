from wagtail import blocks
from etna.core.blocks.image import APIImageChooserBlock


class ShopCollectionBlock(blocks.StructBlock):
    """
    Block for promoting a shop collection (usually Shopify).
    """

    title = blocks.CharBlock(
        label="Title",
        max_length=100,
    )

    description = blocks.CharBlock(
        label="Description",
        max_length=255,
    )

    url = blocks.URLBlock(
        label="URL",
        help_text="The URL to the shop collection",
    )

    background_image = APIImageChooserBlock(
        label="Background image",
        required=False,
    )

    class Meta:
        icon = "shop"
        label = "Shop collection"
