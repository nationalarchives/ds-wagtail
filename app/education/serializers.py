from rest_framework import serializers

from app.core.serializers import DefaultPageSerializer, RichTextSerializer


class _StreamFieldRepresentationMixin:
    @staticmethod
    def _serialize_stream_field(instance, field_name):
        field = instance._meta.get_field(field_name)
        stream_value = getattr(instance, field_name)
        return field.stream_block.get_api_representation(stream_value, context={})


class KeyStageSerializer(serializers.Serializer):
    name = serializers.CharField()
    slug = serializers.SlugField()
    stage = serializers.IntegerField(allow_null=True)
    age_range = serializers.CharField(allow_blank=True)
    short_key_stage = serializers.CharField()
    public_age_range = serializers.CharField()


class TimePeriodSerializer(serializers.Serializer):
    name = serializers.CharField()
    slug = serializers.SlugField()
    year_from = serializers.IntegerField(allow_null=True)
    year_to = serializers.IntegerField(allow_null=True)


class ThemeSerializer(serializers.Serializer):
    name = serializers.CharField()
    slug = serializers.SlugField()


class SourceSerializer(_StreamFieldRepresentationMixin, serializers.Serializer):
    def to_representation(self, instance):
        if not instance:
            return None

        return {
            "title": instance.title,
            "media": self._serialize_stream_field(instance, "media"),
            "featured_link": self._serialize_stream_field(instance, "featured_link"),
            "description": self._serialize_stream_field(instance, "description"),
            "question": self._serialize_stream_field(instance, "question"),
        }


class CurriculumConnectionSerializer(
    _StreamFieldRepresentationMixin, serializers.Serializer
):
    def to_representation(self, instance):
        if not instance:
            return None

        return {
            "title": instance.title,
            "media": self._serialize_stream_field(instance, "media"),
            "featured_link": self._serialize_stream_field(instance, "featured_link"),
            "description": self._serialize_stream_field(instance, "description"),
            "question": self._serialize_stream_field(instance, "question"),


class SessionLocationSerializer(serializers.Serializer):
    def to_representation(self, instance):
        if not instance:
            return None

        return {
            "location_type": instance.location_type,
            "location_type_display": instance.get_location_type_display()
            if instance.location_type
            else None,
            "duration": instance.duration,
            "region": instance.region,
            "region_display": instance.get_region_display()
            if instance.region
            else None,
            "venue_name": instance.venue_name,
            "address_line_1": instance.address_line_1,
            "address_line_2": instance.address_line_2,
            "postcode": instance.postcode,
        }


class LinkedPageSerializer(serializers.Serializer):
    def to_representation(self, instance):
        if not instance:
            return None

        return {
            "selected_page": DefaultPageSerializer().to_representation(
                instance.selected_page
            )
        }
