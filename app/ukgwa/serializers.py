from app.core.serializers import DefaultPageSerializer
from rest_framework import serializers


class SubpagesSerializer(serializers.Serializer):
    def to_representation(self, queryset):
        return [DefaultPageSerializer().to_representation(page) for page in queryset]
