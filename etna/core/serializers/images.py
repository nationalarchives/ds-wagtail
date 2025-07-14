from rest_framework.serializers import Serializer

from etna.ciim.client import CIIMClient


def image_generator(
    original_image,
    rendition_size="fill-600x400",
    jpeg_quality=60,
    webp_quality=60,
    background_colour=None,
    additional_formats=[],
):
    background_colour_rendition = (
        f"|bgcolor-{background_colour}" if background_colour else ""
    )
    jpeg_image = original_image.get_rendition(
        f"{rendition_size}|format-jpeg|jpegquality-{jpeg_quality}{background_colour_rendition}"
    )
    webp_image = original_image.get_rendition(
        f"{rendition_size}|format-webp|webpquality-{webp_quality}{background_colour_rendition}"
    )

    additional_images = {}

    if formats := additional_formats:
        for format in formats:
            additional_image = original_image.get_rendition(
                f"{rendition_size}|format-{format}"
            )
            if additional_image:
                additional_image = {
                    "url": additional_image.url,
                    "full_url": additional_image.full_url,
                    "width": additional_image.width,
                    "height": additional_image.height,
                }
                additional_images[format] = additional_image

    if not jpeg_image or not webp_image:
        return None

    return {
        "jpeg": {
            "url": jpeg_image.url,
            "full_url": jpeg_image.full_url,
            "width": jpeg_image.width,
            "height": jpeg_image.height,
        },
        "webp": {
            "url": webp_image.url,
            "full_url": webp_image.full_url,
            "width": webp_image.width,
            "height": webp_image.height,
        },
        **(additional_images),
    }


class ImageSerializer(Serializer):
    """
    This ImageSerializer was created to improve the `ImageRenditionField` that
    comes as part of the Wagtail API. This serializer allows us to create a
    JPEG and WEBP rendition in one field, rather than having to have multiple fields.

    rendition_size defaults to `fill-600x400`, but can be specified
    when the serializer is used, e.g:
    ImageSerializer(rendition_size="original")

    jpeg_quality and webp_quality default to 60 and 80 respectively,
    and can be specified in the same way as rendition_size.

    additional_formats is an optional list of additional formats to generate,
    such as `png`, `gif`, etc. These will be returned in the API response
    in the same way as the `jpeg` and `webp` renditions.

    The source of the image can also be set in the serializer, e.g:
    APIField("image_large", serializer=ImageSerializer(rendition_size="fill-900x900", source="image"))

    This will come back as `image_large` in the API response.
    """

    def __init__(
        self,
        rendition_size="fill-600x400",
        jpeg_quality=60,
        webp_quality=60,
        background_colour="fff",
        additional_formats=[],
        *args,
        **kwargs,
    ):
        self.rendition_size = rendition_size
        self.jpeg_quality = jpeg_quality
        self.webp_quality = webp_quality
        self.background_colour = background_colour
        self.additional_formats = additional_formats
        super().__init__(*args, **kwargs)

    def to_representation(self, value):
        if value:
            image_data = image_generator(
                original_image=value,
                rendition_size=self.rendition_size,
                jpeg_quality=self.jpeg_quality,
                webp_quality=self.webp_quality,
                background_colour=self.background_colour,
                additional_formats=self.additional_formats,
            )

            if not image_data:
                return None

            return {
                "id": value.id,
                "uuid": value.uuid,
                "title": value.title,
                "description": value.description,
                **(image_data),
            }
        return None


class DetailedImageSerializer(ImageSerializer):
    """
    This serializer extends `ImageSerializer` to display extra details on an image,
    such as copyright, and sensitive warnings.

    Generally for in-page image use, rather than secondary page images (teaser images).
    """

    def to_representation(self, value):
        representation = super().to_representation(value)
        if representation:
            representation.update(
                {
                    "transcript": (
                        {
                            "heading": value.get_transcription_heading_display(),
                            "text": value.transcription,
                        }
                        if value.transcription
                        else None
                    ),
                    "translation": (
                        {
                            "heading": value.get_translation_heading_display(),
                            "text": value.translation,
                        }
                        if value.translation
                        else None
                    ),
                    "copyright": value.copyright if value.copyright else None,
                }
            )
        return representation
