from app.core.serializers import DefaultPageSerializer
from rest_framework import serializers


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
    public_key_stage = serializers.CharField()
    short_key_stage = serializers.CharField()
    public_age_range = serializers.CharField()


class TimePeriodSerializer(serializers.Serializer):
    name = serializers.CharField()
    slug = serializers.SlugField()
    date_from = serializers.DateField(allow_null=True)
    date_to = serializers.DateField(allow_null=True)


class ThemeSerializer(serializers.Serializer):
    name = serializers.CharField()
    slug = serializers.SlugField()


class SourceSerializer(_StreamFieldRepresentationMixin, serializers.Serializer):
    def to_representation(self, instance):
        if not instance:
            return None

        return {
            "title": instance.title,
            "image": self._serialize_stream_field(instance, "image"),
            "media": self._serialize_stream_field(instance, "media"),
            "youtube": self._serialize_stream_field(instance, "youtube"),
            "media_caption": self._serialize_stream_field(instance, "media_caption"),
            "source_featured_link": self._serialize_stream_field(
                instance, "source_featured_link"
            ),
            "source_featured_external_link": (instance.source_featured_external_link),
            "description": self._serialize_stream_field(instance, "description"),
            "question": self._serialize_stream_field(instance, "question"),
        }


# TODO: make more generic to use as a further links that can be overridden
class EducationReadMoreLinkSerializer(serializers.Serializer):
    def to_representation(self, instance):
        if not instance:
            return None

        return {
            "selected_page": DefaultPageSerializer().to_representation(
                instance.selected_page
            )
        }
