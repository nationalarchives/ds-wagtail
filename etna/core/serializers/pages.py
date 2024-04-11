from wagtail.images.api.fields import ImageRenditionField

from rest_framework import serializers


def get_api_fields(object, required_api_fields:list=[]) -> list:
    """
    Get the selected fields (required_api_fields) from the object's api_fields
    attribute, and return them as a list of APIField instances. APIFields are
    useful as they contain the name of the field, and the serializer to use
    to convert the data to something useful.

    If you want fields to appear in the list returned by this function,
    but not in the API representation of a page, you should add them to the
    `default_api_fields` attribute of the page model.
    """
    fields = []
    if default_api_fields := object.default_api_fields:
        fields.extend(default_api_fields)
    if api_fields := object.api_fields:
        for field in required_api_fields:
            for api_field in api_fields:
                if field == api_field.name:
                    fields.append(api_field)
                    break
    return fields

def get_field_data(object, field) -> any:
    """
    This function takes an object and an APIField instance, and returns 
    the serialized data for that field from the object.
    """
    if object:
        field_data = getattr(object, field.name, None)
        if serializer := field.serializer:
            if source := serializer.source:
                field_data = serializer.to_representation(getattr(object, source, None))
            else:
                field_data = serializer.to_representation(field_data)
        if callable(field_data):
            field_data = field_data()
        return field_data
    return None

def get_api_data(object, required_api_fields:list=[]) -> dict:
    """
    This function takes a list of required_api_fields which are the fields
    to be passed to the `get_api_fields` function, and then uses the list
    returned by that function to build an API representation of the object.
    This makes use of the APIField instances that are returned, by using the
    serializers that are attached to them to convert the data to something
    useful to the front-end.
    """
    api_representation = {}
    if object:
        specific = object.specific
        if api_fields := get_api_fields(object=specific, required_api_fields=required_api_fields):
            for field in api_fields:
                api_representation[field.name] = get_field_data(object=specific, field=field)
    return api_representation


class LinkedPageSerializer(serializers.ModelSerializer):
    """
    This Serializer should be inherited as a base class for all "linked" or "secondary"
    page serializers. It provides a common set of fields that are useful for
    serializing linked pages - otherwise it only provides a page ID.

    Fields returned must be set in the `Meta.fields` attribute of the subclass.
    """

    def teaser_images(
        rendition_size: str,
        jpeg_quality: str,
        webp_quality: int,
        source: str = "teaser_image",
        quality: int = 80,
    ):
        """
        This method returns a tuple of two ImageRenditionField instances for the
        given rendition size, JPEG quality and WebP quality. The source parameter
        is used to specify the source image field to use for the rendition.

        To override the default rendition size, quality, or source, you should
        override this in the subclass, following the same structure as teaser_image_jpeg
        and teaser_image_webp below. This will allow for flexibility around the
        types of images that we can supply on a case-by-case basis.

        Args:
        rendition_size: The size of the rendition to return.
        jpeg_quality: The quality of the JPEG rendition.
        webp_quality: The quality of the WebP rendition.
        source: The source image field to use for the rendition - defaults to "teaser_image" if un-set.
        quality: The quality to use for the rendition - only used if no jpeg or webp_quality is set.
        """
        return (
            ImageRenditionField(
                f"{rendition_size}|format-jpeg|jpegquality-{jpeg_quality or quality}",
                source=source,
            ),
            ImageRenditionField(
                f"{rendition_size}|format-webp|webpquality-{webp_quality or quality}",
                source=source,
            ),
        )

    title = serializers.CharField()
    url = serializers.SerializerMethodField()
    full_url = serializers.URLField()
    teaser_image_jpeg, teaser_image_webp = teaser_images(
        rendition_size="fill-600x400", jpeg_quality=60, webp_quality=80
    )

    def get_url(self, obj):
        return obj.get_url()
