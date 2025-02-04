from rest_framework import serializers


class TaggableSerializer(serializers.CharField):
    """
    This Serializer should be used to serialize an instance
    of ClusterTaggableManager. ClusterTaggableManager is not
    JSON serializable, so we need to convert it to a list of
    tag names.
    """

    def to_representation(self, instance):
        return [tag.name for tag in instance.all()]


class MourningSerializer(serializers.Serializer):
    def to_representation(self, instance):
        return {
            "title": instance.title,
            "message": instance.message,
        }
