from wagtail.rich_text import expand_db_html

from rest_framework import serializers


class RichTextSerializer(serializers.CharField):
    """
    Serializer for rich text fields.
    """

    def to_representation(self, value):
        representation = super().to_representation(value)
        return expand_db_html(representation)
