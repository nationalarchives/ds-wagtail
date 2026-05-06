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


class TimePeriodSerializer(serializers.Serializer):
    name = serializers.CharField()
    slug = serializers.SlugField()


class ThemeSerializer(serializers.Serializer):
    name = serializers.CharField()
    slug = serializers.SlugField()


class CurriculumConnectionSerializer(
    _StreamFieldRepresentationMixin, serializers.Serializer
):
    def to_representation(self, instance):
        if not instance:
            return None

        return {
            "key_stage": KeyStageSerializer().to_representation(instance.key_stage),
            "connection_description": self._serialize_stream_field(
                instance, "curriculum_connection_description"
            ),
        }


class SourceSerializer(_StreamFieldRepresentationMixin, serializers.Serializer):
    def to_representation(self, instance):
        if not instance:
            return None

        return {
            "source_title": instance.source_title,
            "source_image": self._serialize_stream_field(instance, "source_image"),
            "source_media": self._serialize_stream_field(instance, "source_media"),
            "source_youtube": self._serialize_stream_field(instance, "source_youtube"),
            "source_media_caption": self._serialize_stream_field(
                instance, "source_media_caption"
            ),
            "source_media_featured_link": self._serialize_stream_field(
                instance, "source_media_featured_link"
            ),
            "source_media_featured_external_link": (
                instance.source_media_featured_external_link
            ),
            "source_description": self._serialize_stream_field(
                instance, "source_description"
            ),
            "source_question": self._serialize_stream_field(
                instance, "source_question"
            ),
        }


class EducationReadMoreLinkSerializer(serializers.Serializer):
    def to_representation(self, instance):
        if not instance:
            return None

        return {
            "selected_page": DefaultPageSerializer().to_representation(
                instance.selected_page
            )
        }
