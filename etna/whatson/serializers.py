from rest_framework import serializers

from etna.core.serializers import (
    DefaultPageSerializer,
    ImageSerializer,
    RichTextSerializer,
)


class EventTypeSerializer(serializers.Serializer):
    """Serializer for the EventType model."""

    def to_representation(self, instance):
        if instance:
            return instance.name
        return None


class WhatsOnPageSelectionSerializer(serializers.Serializer):
    """Serializer for the WhatsOnPageSelection model."""

    def to_representation(self, instance):
        if instance:
            return {
                "selected_page": DefaultPageSerializer(
                    required_api_fields=["featured_page", "latest_listings"]
                ).to_representation(instance.selected_page),
            }
        return None


class SpeakerSerializer(serializers.Serializer):
    """Serializer for the EventSpeaker model."""

    def to_representation(self, instance):
        if instance:
            if instance.person_page:
                representation = DefaultPageSerializer().to_representation(
                    instance.person_page
                )
                representation["biography"] = RichTextSerializer().to_representation(
                    instance.biography
                )
                return representation
            return {
                "name": instance.name,
                "role": instance.role,
                "biography": RichTextSerializer().to_representation(instance.biography),
                "image": ImageSerializer(
                    rendition_size="fill-400x400"
                ).to_representation(instance.image),
                "image_small": ImageSerializer(
                    rendition_size="fill-128x128"
                ).to_representation(instance.image),
            }
        return None


class SessionSerializer(serializers.Serializer):
    """Serializer for the EventSession model."""

    def to_representation(self, instance):
        if instance:
            return {
                "start": instance.start.isoformat() if instance.start else None,
                "end": instance.end.isoformat() if instance.end else None,
                "sold_out": instance.sold_out,
            }
