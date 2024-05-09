from rest_framework.serializers import Serializer


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

    The source of the image can also be set in the serializer, e.g:
    APIField("image_large", serializer=ImageSerializer(rendition_size="fill-900x900", source="image"))

    This will come back as `image_large` in the API response.
    """

    def __init__(
        self,
        rendition_size="fill-600x400",
        jpeg_quality=60,
        webp_quality=80,
        *args,
        **kwargs,
    ):
        self.jpeg_quality = jpeg_quality
        self.webp_quality = webp_quality
        self.rendition_size = rendition_size
        super().__init__(*args, **kwargs)

    def to_representation(self, value):
        if value:
            jpeg_image = value.get_rendition(
                f"{self.rendition_size}|format-jpeg|jpegquality-{self.jpeg_quality}"
            )
            webp_image = value.get_rendition(
                f"{self.rendition_size}|format-webp|webpquality-{self.webp_quality}"
            )

            return {
                "id": value.id,
                "title": value.title,
                "image_jpeg": {
                    "url": jpeg_image.url,
                    "full_url": jpeg_image.full_url,
                    "width": jpeg_image.width,
                    "height": jpeg_image.height,
                },
                "image_webp": {
                    "url": webp_image.url,
                    "full_url": webp_image.full_url,
                    "width": webp_image.width,
                    "height": webp_image.height,
                },
            }
        return None


class DetailedImageSerializer(ImageSerializer):
    """
    This serializer extends `ImageSerializer` to display extra details on an image,
    such as copyright, and sensitive warnings.

    Generally for in-page image use, rather than secondary page images.
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
                    "is_sensitive": value.is_sensitive,
                    "custom_sensitive_image_warning": (
                        value.custom_sensitive_image_warning
                        if value.custom_sensitive_image_warning
                        else None
                    ),
                }
            )
        return representation


class HighlightImageSerializer(DetailedImageSerializer):
    """
    This serializer extends `DetailedImageSerializer` to display details on
    an image that are used for `Highlights`.
    """

    def to_representation(self, value):
        representation = super().to_representation(value)
        if representation:
            representation.update(
                {
                    "description": value.description,
                    "record": value.record.iaid,
                    "record_dates": value.record_dates,
                }
            )
        return representation
