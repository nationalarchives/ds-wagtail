from wagtail.images.api.v2.serializers import ImageSerializer
from wagtail.images.api.v2.views import ImagesAPIViewSet

from etna.core.serializers.images import image_generator


class ViewSetImageSerializer(ImageSerializer):
    """
    Serializer for images in the /images endpoint.
    """

    rendition_size = "max-900x900"
    jpeg_quality = 60
    webp_quality = 60
    background_colour = "fff"
    additional_formats = []

    def to_representation(self, value):
        representation = super().to_representation(value)

        image_data = image_generator(
            original_image=value,
            rendition_size=self.rendition_size,
            jpeg_quality=self.jpeg_quality,
            webp_quality=self.webp_quality,
            background_colour=self.background_colour,
            additional_formats=self.additional_formats,
        )

        return representation | image_data


class CustomImagesAPIViewSet(ImagesAPIViewSet):
    base_serializer_class = ViewSetImageSerializer
    body_fields = ImagesAPIViewSet.body_fields + [
        "uuid",
        "title",
        "file",
        "copyright",
        "is_sensitive",
        "custom_sensitive_image_warning",
        "tags",
        "transcription_heading",
        "transcription",
        "translation_heading",
        "translation",
        "record",
        "record_dates",
        "description",
    ]
