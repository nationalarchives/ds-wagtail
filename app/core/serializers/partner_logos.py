from rest_framework import serializers

from .images import ImageSerializer


class PartnerLogoSerializer(serializers.Serializer):
    """
    Serializer for PartnerLogo model.
    """

    image_serializer = ImageSerializer(
        rendition_size="max-400x200",
        background_colour=None,
    )

    def to_representation(self, instance):
        return {
            "name": instance.name,
            "logo": (
                self.image_serializer.to_representation(instance.logo)
                if instance.logo
                else None
            ),
            "logo_dark": (
                self.image_serializer.to_representation(instance.logo_dark)
                if instance.logo_dark
                else None
            ),
        }
