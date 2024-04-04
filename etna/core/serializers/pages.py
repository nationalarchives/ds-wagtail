from .images import generate_teaser_images
from wagtail.models import Page
from rest_framework import serializers
from django.db.models import QuerySet
from etna.images.models import CustomImage


def generate_images(image, field_name="teaser_image", rendition_size="fill-600x400", jpeg_quality=60, webp_quality=80):
    """
    Generate the fields required for an image item with the given rendition size
    and quality settings.
    """
    jpeg_image = image.get_rendition(
        f"{rendition_size or "fill-600x400"}|format-jpeg|jpegquality-{jpeg_quality or 60}"
    )
    webp_image = image.get_rendition(
        f"{rendition_size or "fill-600x400"}|format-webp|webpquality-{webp_quality or 80}"
    )
    return {f"{field_name}_jpeg": {
        "url": jpeg_image.url,
        "full_url": jpeg_image.full_url,
        "width": jpeg_image.width,
        "height": jpeg_image.height,
    },
    f"{field_name}_webp": {
        "url": webp_image.url,
        "full_url": webp_image.full_url,
        "width": webp_image.width,
        "height": webp_image.height,
    }}

def get_nested_data(value, field_path):
    attrs = field_path.split(".")
    nested_obj = getattr(value, attrs[0], None)
    nested_data = {attrs[0]: None}
    if isinstance(nested_obj, (list, tuple, QuerySet)):
        nested_list = []
        for obj in nested_obj:
            try:
                specific_obj = obj.specific
            except AttributeError:
                specific_obj = obj

            for nested_attr in attrs[1:]:
                field_data = getattr(specific_obj, nested_attr, None)
                if isinstance(field_data, CustomImage):
                    field_data = generate_images(field_data, field_name=nested_attr)
                nested_list.append({nested_attr: field_data})
        nested_data[attrs[0]] = nested_list
    else:
        for nested_attr in attrs[1:]:
            nested_data.append(getattr(nested_obj, nested_attr, None))
    return nested_data


def get_api_fields(value, api_fields=[], **kwargs):
    if not value:
        return None
    
    specific = value.specific
    api_field_data = {}
    for attr in api_fields:
        if "." in attr:
            if field_data := api_field_data.get(attr.split(".")[0]):
                for index, item in enumerate(get_nested_data(specific, attr).get(attr.split(".")[0])):
                    other_data = get_nested_data(specific, attr).get(attr.split(".")[0])[index]
                    field_data[index].update(other_data) 
            else:
                api_field_data.update(get_nested_data(specific, attr))
        else:
            field_data = getattr(specific, attr, None)
            if callable(field_data):
                api_field_data[attr] = field_data()
            elif isinstance(field_data, Page):
                api_field_data[attr] = get_api_fields(field_data)
            elif isinstance(field_data, (list, tuple)):
                try:
                    api_field_data[attr] = [get_api_fields(item) for item in field_data]
                except AttributeError:
                    pass
            elif isinstance(field_data, CustomImage):
                api_field_data.update(generate_images(image=field_data, field_name=attr, rendition_size=kwargs.get("rendition_size", None), jpeg_quality=kwargs.get("jpeg_quality", None), webp_quality=kwargs.get("webp_quality", None)))
    
    # Remove any None/null values from the dictionary
    api_field_data = {key: value for key, value in api_field_data.items() if value is not None}

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
