from django.conf import settings
from rest_framework import serializers

from .images import ImageSerializer


class PartnerLogoSerializer(serializers.Serializer):
    """
    Serializer for PartnerLogo model.
    """

    def to_representation(self, instance):
        return {
            "name": instance.name,
            "image": (
                (settings.WAGTAILADMIN_BASE_URL + instance.svg_file.url)
                if instance.svg_file
                else (
                    ImageSerializer().to_representation(instance.raster_file)
                    if instance.raster_file
                    else None
                )
            ),
            "image_dark": (
                (settings.WAGTAILADMIN_BASE_URL + instance.svg_file_dark.url)
                if instance.svg_file_dark
                else (
                    ImageSerializer().to_representation(instance.raster_file_dark)
                    if instance.raster_file_dark
                    else None
                )
            ),
            "alt_text": instance.alt_text,
        }
