from rest_framework import serializers

from .images import ImageSerializer

image_serializer = ImageSerializer(
    rendition_size="max-400x200",
    background_colour=None,
    jpeg_quality=100,
    webp_quality=100,
)


class PartnerLogoSerializer(serializers.Serializer):
    """
    Serializer for PartnerLogo model.
    """

    def to_representation(self, instance):
        return {
            "name": instance.name,
            "logo": (
                image_serializer.to_representation(instance.logo)
                if instance.logo
                else None
            ),
            "logo_dark": (
                image_serializer.to_representation(instance.logo_dark)
                if instance.logo_dark
                else None
            ),
        }
