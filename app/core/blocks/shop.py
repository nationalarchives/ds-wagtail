from wagtail import blocks

from app.core.blocks.image import APIImageChooserBlock


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

    cta_text = blocks.CharBlock(
        label="CTA text",
        max_length=50,
        default="Shop now",
    )

    url = blocks.URLBlock(
        label="URL",
        help_text="The URL to the shop collection",
    )

    background_image = APIImageChooserBlock(
        label="Background image",
    )

    class Meta:
        icon = "shop"
        label = "Shop collection"
