from rest_framework import serializers

from .client import CIIMClient


class RecordSerializer(serializers.Serializer):
    def to_representation(self, instance):
        default_params = {
            "id": instance,
        }
        client = CIIMClient(default_params=default_params)

        return client.get_serialized_record()
