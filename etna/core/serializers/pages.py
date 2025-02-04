from rest_framework import serializers
from rest_framework.fields import empty


def get_api_fields(object, required_api_fields: list = []) -> list:
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


def get_api_data(object, required_api_fields: list = []) -> dict:
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
        if api_fields := get_api_fields(
            object=specific, required_api_fields=required_api_fields
        ):
            for field in api_fields:
                api_representation[field.name] = get_field_data(
                    object=specific, field=field
                )
    return api_representation or None


class DefaultPageSerializer(serializers.Serializer):
    def __init__(self, instance=None, data=empty, required_api_fields=[], **kwargs):
        self.required_api_fields = required_api_fields
        super().__init__(instance=instance, data=data, **kwargs)

    def to_representation(self, instance):
        return get_api_data(instance, required_api_fields=self.required_api_fields)


class SimplePageSerializer(serializers.Serializer):
    def to_representation(self, instance):
        return {
            "id": instance.id,
            "title": instance.title,
            "teaser_text": instance.teaser_text,
            "url": instance.url,
            "full_url": instance.full_url,
        }


class AliasOfSerializer(serializers.Serializer):
    """
    A serializer used to override the default representation of an alias page,
    to include information that can decide is necessary for the front-end.
    """

    def to_representation(self, instance):
        return {
            "id": instance.id,
            "url": instance.url,
        }
