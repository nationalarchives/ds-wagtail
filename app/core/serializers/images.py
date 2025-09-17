from rest_framework.serializers import Serializer


def image_generator(
    original_image,
    rendition_size="fill-600x400",
    jpeg_quality=60,
    webp_quality=70,
    background_colour=None,
    formats=["jpeg", "webp"],
):
    if not original_image:
        return None

    background_colour_rendition = (
        f"|bgcolor-{background_colour}" if background_colour else ""
    )

    rendition_specs = []
    for fmt in formats:
        if fmt == "jpeg":
            rendition_specs.append(
                f"{rendition_size}|format-jpeg|jpegquality-{jpeg_quality}{background_colour_rendition}"
            )
        elif fmt == "webp":
            rendition_specs.append(
                f"{rendition_size}|format-webp|webpquality-{webp_quality}{background_colour_rendition}"
            )
        else:
            rendition_specs.append(f"{rendition_size}|format-{fmt}")

    renditions = original_image.get_renditions(*rendition_specs)

    if not renditions:
        return None

    output = {}
    for spec, rendition in renditions.items():
        fmt = spec.split("format-")[1].split("|", 1)[0]
        output[fmt] = {
            "url": rendition.url,
            "full_url": rendition.full_url,
            "width": rendition.width,
            "height": rendition.height,
        }

    return output


class ImageSerializer(Serializer):
    """
    This ImageSerializer was created to improve the `ImageRenditionField` that
    comes as part of the Wagtail API. This serializer allows us to create a
    JPEG and WEBP rendition in one field, rather than having to have multiple fields.

    rendition_size defaults to `fill-600x400`, but can be specified
    when the serializer is used, e.g:
    ImageSerializer(rendition_size="original")

    jpeg_quality and webp_quality default to 60 and 70 respectively,
    and can be specified in the same way as rendition_size.

    To generate any additional formats of images, override `formats` in the serializer, e.g:
    ["jpeg", "webp", "png"]. These will be returned in the API response
    in the same way as the `jpeg` and `webp` renditions.

    The source of the image can also be set in the serializer, e.g:
    APIField("image_large", serializer=ImageSerializer(rendition_size="fill-900x900", source="image"))

    This will come back as `image_large` in the API response.
    """

    def __init__(
        self,
        rendition_size="fill-600x400",
        jpeg_quality=60,
        webp_quality=70,
        background_colour="fff",
        formats=["jpeg", "webp"],
        *args,
        **kwargs,
    ):
        self.rendition_size = rendition_size
        self.jpeg_quality = jpeg_quality
        self.webp_quality = webp_quality
        self.background_colour = background_colour
        self.formats = formats
        super().__init__(*args, **kwargs)

    def to_representation(self, value):
        if value:
            image_data = image_generator(
                original_image=value,
                rendition_size=self.rendition_size,
                jpeg_quality=self.jpeg_quality,
                webp_quality=self.webp_quality,
                background_colour=self.background_colour,
                formats=self.formats,
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
