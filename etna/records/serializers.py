from rest_framework import serializers


class RecordSerializer(serializers.Serializer):
    def to_representation(self, instance):
        return {
            "title": instance.summary_title,
            "iaid": instance.iaid,
            "reference_number": instance.reference_number,
        }
