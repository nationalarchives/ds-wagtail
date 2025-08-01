from django.conf import settings
from wagtail import blocks
from wagtail.images.blocks import ImageChooserBlock

from app.core.blocks.paragraph import APIRichTextBlock
from app.core.serializers.images import DetailedImageSerializer


class APIImageChooserBlock(ImageChooserBlock):
    """
    APIImageChooserBlock inherits ImageChooserBlock and adds the ability
    to generate different renditions for JPEG and WebP formats. Without
    this, and the get_api_representation override, the API would return
    the database entry - which is just an image ID. This would require
    a second API call to get the image renditions.

    rendition_size defaults to `fill-600x400`, but can be specified
    when the block is used, e.g:
    image = APIImageChooserBlock(rendition_size="original")

    jpeg_quality and webp_quality default to 60 and 80 respectively,
    and can be specified in the same way as rendition_size.
    """

    def __init__(
        self,
        required=True,
        help_text=None,
        rendition_size="fill-600x400",
        jpeg_quality=60,
        webp_quality=60,
        background_colour="fff",
        **kwargs,
    ):
        self.rendition_size = rendition_size
        self.jpeg_quality = jpeg_quality
        self.webp_quality = webp_quality
        self.background_colour = background_colour
        super().__init__(required=required, help_text=help_text, **kwargs)

    def get_api_representation(self, value, context=None):
        serializer = DetailedImageSerializer(
            rendition_size=self.rendition_size,
            jpeg_quality=self.jpeg_quality,
            webp_quality=self.webp_quality,
            background_colour=self.background_colour,
        )
        return serializer.to_representation(value)


class ContentImageBlock(blocks.StructBlock):
    image = APIImageChooserBlock(rendition_size="max-900x900", required=True)
    caption = APIRichTextBlock(
        features=["bold", "italic", "link"],
        help_text=(
            "If provided, displays directly below the image. Can be used to specify sources, transcripts or "
            "other useful metadata."
        ),
        label="Caption (optional)",
        required=False,
    )

    class Meta:
        label = "Image"
        icon = "image"


class ImageGalleryBlock(blocks.StructBlock):
    title = blocks.CharBlock(required=False)
    description = APIRichTextBlock(
        required=False, features=settings.INLINE_RICH_TEXT_FEATURES
    )
    images = blocks.ListBlock(ContentImageBlock())

    def get_api_representation(self, value, context=None):
        representation = super().get_api_representation(value, context)
        representation["count"] = len(value["images"])
        return representation

    class Meta:
        label = "Image Gallery"
        icon = "image"
