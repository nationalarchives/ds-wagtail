from rest_framework import serializers
from wagtail.images.api.fields import ImageRenditionField

class LinkedPageSerializer(serializers.ModelSerializer):
    """
    This Serializer should be inherited as a base class for all "linked" or "secondary"
    page serializers. It provides a common set of fields that are useful for
    serializing linked pages - otherwise it only provides a page ID.

    Fields returned must be set in the `Meta.fields` attribute of the subclass.
    """
    def teaser_images(rendition_size, jpeg_quality, webp_quality, source="teaser_image", quality=80):
        return (
            ImageRenditionField(f"{rendition_size}|format-jpeg|jpegquality-{jpeg_quality or quality}", source=source),
            ImageRenditionField(f"{rendition_size}|format-webp|webpquality-{webp_quality or quality}", source=source),
        )
    
    title = serializers.CharField()
    url_path = serializers.SerializerMethodField()
    full_url = serializers.URLField()
    teaser_image_jpeg, teaser_image_webp = teaser_images(rendition_size="fill-600x400", jpeg_quality=60, webp_quality=80)

    def get_url_path(self, obj):
        return obj.get_url()
    
    