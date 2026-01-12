from app.core.blocks.image import APIImageChooserBlock
from app.core.serializers import ImageSerializer
from wagtail import blocks


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
        rendition_size="fill-1800x720",
    )

    def get_api_representation(self, value, context=None):
        representation = super().get_api_representation(value, context)
        if background_image := value.get("background_image"):
            representation["background_image_small"] = ImageSerializer(
                rendition_size="fill-600x400"
            ).to_representation(background_image)
        return representation

    class Meta:
        icon = "shop"
        label = "Shop collection"
