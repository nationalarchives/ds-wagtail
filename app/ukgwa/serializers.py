from app.core.serializers import DefaultPageSerializer
from rest_framework import serializers


class SubpagesSerializer(serializers.Serializer):
    def to_representation(self, queryset):
        return [DefaultPageSerializer().to_representation(page) for page in queryset]


class ArchiveSearchComponentSerializer(serializers.Serializer):
    def to_representation(self, instance):
        if instance:
            return {
                "heading": instance.heading,
                "help_text": instance.help_text,
                "button_text": instance.button_text,
                "archive_type": instance.archive_type,
            }
        return None


class ArchiveRecordSerializer(serializers.Serializer):
    """Serializer for ArchiveRecord model"""

    id = serializers.IntegerField(source="wam_id")
    profile_name = serializers.CharField()
    record_url = serializers.URLField()
    archive_link = serializers.URLField()
    domain_type = serializers.CharField()
    first_capture_display = serializers.CharField()
    latest_capture_display = serializers.CharField()
    ongoing = serializers.BooleanField()
    sort_name = serializers.CharField()
    first_character = serializers.CharField()

    class Meta:
        fields = [
            "id",
            "profile_name",
            "record_url",
            "archive_link",
            "domain_type",
            "first_capture_display",
            "latest_capture_display",
            "ongoing",
            "sort_name",
            "first_character",
        ]
