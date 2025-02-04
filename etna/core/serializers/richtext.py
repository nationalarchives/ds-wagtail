from rest_framework import serializers
from wagtail.rich_text import expand_db_html


class RichTextSerializer(serializers.CharField):
    """
    Serializer for rich text fields.
    """

    def to_representation(self, value):
        representation = super().to_representation(value)
        return expand_db_html(representation)
