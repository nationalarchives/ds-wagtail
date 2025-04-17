from rest_framework import serializers

from .client import CIIMClient


class RecordSerializer(serializers.Serializer):
    def to_representation(self, instance):
        params = {
            "id": instance,
        }
        client = CIIMClient(params=params)

        return client.get_serialized_record()
