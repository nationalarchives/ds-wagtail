from rest_framework import serializers
from .images import ImageSerializer

class PartnerLogoSerializer(serializers.Serializer):
    """
    Serializer for PartnerLogo model.
    """

    def to_representation(self, instance):
        return {
            "name": instance.name,
            "image": instance.full_url if instance.svg_file else ImageSerializer(instance.raster_file).data if instance.raster_file else None,
            "alt_text": instance.alt_text,
        }