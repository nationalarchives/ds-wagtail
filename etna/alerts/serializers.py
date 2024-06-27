from rest_framework import serializers
from wagtail.rich_text import expand_db_html


class AlertSerializer(serializers.Serializer):
    def to_representation(self, instance):
        return {
            "title": instance.title,
            "message": expand_db_html(instance.message),
            "alert_level": instance.alert_level,
        }
