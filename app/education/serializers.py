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
