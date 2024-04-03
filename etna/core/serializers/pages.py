from .images import generate_teaser_images
from wagtail.models import Page
from rest_framework import serializers

def get_api_fields(value, api_fields=[], **kwargs):
    if not value:
        return None
    
    if not "teaser_image" in api_fields and (kwargs.get("rendition_size", None) or kwargs.get("jpeg_quality", None) or kwargs.get("webp_quality", None)):
        raise ValueError("rendition_size, jpeg_quality or webp_quality, can't be set if there is no teaser_image in api_fields")

    specific = value.specific
    
    api_field_data = {}
    for attr in api_fields:
        api_field_data[attr] = getattr(specific, attr, None)
        if callable(api_field_data[attr]):
            api_field_data[attr] = api_field_data[attr]()
        elif isinstance(api_field_data[attr], Page):
            api_field_data[attr] = get_api_fields(api_field_data[attr])
        elif isinstance(api_field_data[attr], (list, tuple)):
            api_field_data[attr] = [get_api_fields(item) for item in api_field_data[attr]]
        print(api_field_data[attr])

    if api_field_data.get("teaser_image"):
        jpeg_image = api_field_data["teaser_image"].get_rendition(
            f"{kwargs.get("rendition_size", None) or "fill-600x400"}|format-jpeg|jpegquality-{kwargs.get("jpeg_quality", None) or 60}"
        )
        webp_image = api_field_data["teaser_image"].get_rendition(
            f"{kwargs.get("rendition_size", None) or "fill-600x400"}|format-webp|webpquality-{kwargs.get("webp_quality", None) or 80}"
        )
        api_field_data.pop("teaser_image")
        api_field_data["teaser_image_jpeg"] = {
            "url": jpeg_image.url,
            "full_url": jpeg_image.full_url,
            "width": jpeg_image.width,
            "height": jpeg_image.height,
        }
        api_field_data["teaser_image_webp"] = {
            "url": webp_image.url,
            "full_url": webp_image.full_url,
            "width": webp_image.width,
            "height": webp_image.height,
        }

    return {
        "id": specific.id,
        "title": specific.title,
        "url": specific.url,
        "full_url": specific.full_url,
        **api_field_data,
    }

class LinkedPageSerializer(serializers.ModelSerializer):
    """
    This Serializer should be inherited as a base class for all "linked" or "secondary"
    page serializers. It provides a common set of fields that are useful for
    serializing linked pages - otherwise it only provides a page ID.

    Fields returned must be set in the `Meta.fields` attribute of the subclass.
    """


    title = serializers.CharField()
    url = serializers.SerializerMethodField()
    full_url = serializers.URLField()
    teaser_image_jpeg, teaser_image_webp = generate_teaser_images(
        rendition_size="fill-600x400", jpeg_quality=60, webp_quality=80
    )

    def get_url(self, obj):
        return obj.get_url()
