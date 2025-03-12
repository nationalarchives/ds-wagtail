from rest_framework import serializers


class RedirectSerializer(serializers.Serializer):
    def to_representation(self, instance):
        return {
            "id": instance.id,
            "title": instance.title,
            "is_permanent": instance.is_permanent,
            "link": instance.link,
        }
