from rest_framework import serializers
from app.core.serializers.pages import DefaultPageSerializer, get_api_data


class BlogCountSerializer(serializers.Serializer):
    """Serializer for blog post counts"""

    id = serializers.IntegerField()
    posts = serializers.IntegerField()


class MonthlyCountSerializer(serializers.Serializer):
    """Serializer for monthly blog post counts"""

    month = serializers.IntegerField()
    posts = serializers.IntegerField()


class YearlyCountSerializer(serializers.Serializer):
    """Serializer for yearly blog post counts with monthly breakdown"""

    year = serializers.IntegerField()
    posts = serializers.IntegerField()
    months = MonthlyCountSerializer(many=True)


class BlogPostAuthorsSerializer(serializers.Serializer):
    """Serializer for blog post authors with post counts"""

    def to_representation(self, instance):
        """Convert author count dict to proper representation"""
        if isinstance(instance, list):
            result = []
            for item in instance:
                result.append(self._serialize_author_item(item))
            return result
        return self._serialize_author_item(instance)

    @staticmethod
    def _serialize_author_item(item):
        """Serialize a single author count item"""
        return {
            "author": DefaultPageSerializer().to_representation(item.get("author")),
            "posts": item.get("posts", 0),
        }
    