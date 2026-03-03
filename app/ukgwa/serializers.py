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


class BookmarkletCTASerializer(serializers.Serializer):
    def to_representation(self, instance):
        if instance:
            return {
                "heading": instance.heading,
                "body": instance.body,
                "button_text": instance.button_text,
                "button_link": instance.button_link.full_url,
            }
        return None
