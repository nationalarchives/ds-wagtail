from app.core.serializers import RichTextSerializer
from rest_framework import serializers


class KeyStageSerializer(serializers.Serializer):
    name = serializers.CharField()
    slug = serializers.SlugField()


class TimePeriodSerializer(serializers.Serializer):
    name = serializers.CharField()
    slug = serializers.SlugField()


class ThemeSerializer(serializers.Serializer):
    name = serializers.CharField()
    slug = serializers.SlugField()


class CurriculumConnectionSerializer(serializers.Serializer):
    def to_representation(self, instance):
        return {
            "key_stage": KeyStageSerializer().to_representation(instance.key_stage),
            "connection_description": RichTextSerializer().to_representation(
                instance.curriculum_connection_description
            ),
        }
