from rest_framework import serializers
from wagtail.api.v2.serializers import StreamField as StreamFieldSerializer

from app.core.serializers import DefaultPageSerializer, RichTextSerializer


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


class SourceSerializer(serializers.Serializer):
    title = serializers.CharField()
    media = StreamFieldSerializer()
    featured_link = StreamFieldSerializer()
    description = RichTextSerializer()
    question = StreamFieldSerializer()


class CurriculumConnectionSerializer(serializers.Serializer):
    key_stage = KeyStageSerializer()
    description = RichTextSerializer()


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

        return DefaultPageSerializer().to_representation(
            instance.selected_page
        )
