from rest_framework.serializers import Serializer


def image_generator(
    original_image,
    rendition_size: str = "fill-600x400",
    jpeg_quality: int = 60,
    webp_quality: int = 70,
    background_colour: str | None = None,
    formats: list | None = None,
    additional_rendition_specs: dict | None = None,
):
    if formats is None:
        formats = ["jpeg", "webp"]
    if not original_image:
        return None

    background_colour_rendition = (
        f"|bgcolor-{background_colour}" if background_colour else ""
    )

    def build_rendition_spec(size: str, fmt: str) -> str:
        if fmt == "jpeg":
            return (
                f"{size}|format-jpeg|jpegquality-{jpeg_quality}"
                f"{background_colour_rendition}"
            )
        if fmt == "webp":
            return (
                f"{size}|format-webp|webpquality-{webp_quality}"
                f"{background_colour_rendition}"
            )
        return f"{size}|format-{fmt}"

    rendition_specs = []
    output_keys_by_spec = {}

    for fmt in formats:
        spec = build_rendition_spec(rendition_size, fmt)
        rendition_specs.append(spec)
        output_keys_by_spec[spec] = fmt

    if additional_rendition_specs:
        for key, size in additional_rendition_specs.items():
            for fmt in formats:
                spec = build_rendition_spec(size, fmt)
                rendition_specs.append(spec)
                output_keys_by_spec[spec] = f"{key}_{fmt}"

    renditions = original_image.get_renditions(*rendition_specs)

    if not renditions:
        return None

    output = {}
    for spec, rendition in renditions.items():
        output_key = output_keys_by_spec.get(spec)
        if not output_key:
            fmt = spec.split("format-")[1].split("|", 1)[0]
            output_key = fmt

        output[output_key] = {
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
        rendition_size: str = "fill-600x400",
        jpeg_quality: int = 60,
        webp_quality: int = 70,
        background_colour: str = "fff",
        formats: list = None,
        additional_rendition_specs: dict = None,
        *args,
        **kwargs,
    ):
        if formats is None:
            formats = ["jpeg", "webp"]
        self.rendition_size = rendition_size
        self.jpeg_quality = jpeg_quality
        self.webp_quality = webp_quality
        self.background_colour = background_colour
        self.formats = formats
        self.additional_rendition_specs = additional_rendition_specs
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
                additional_rendition_specs=self.additional_rendition_specs,
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
