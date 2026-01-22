from app.api.urls.pages import CustomPagesAPIViewSet
from app.ukgwa.models import ArchiveRecord
from app.ukgwa.serializers import ArchiveRecordSerializer
from django.urls import path
from rest_framework.response import Response


class ArchiveRecordsAPIViewSet(CustomPagesAPIViewSet):
    """
    API ViewSet for archive records.

    Supports filtering by first_character query parameter:
    - /api/v2/archive_records/?first_character=a  (letters a-z)
    - /api/v2/archive_records/?first_character=5  (digits 0-9)
    - /api/v2/archive_records/?first_character=other  (symbols/special chars)

    Returns all matching records (no pagination).
    Note: Frontend should display 'other' as '#' to users.
    """

    def list_view(self, request):
        """
        List archive records filtered by first_character (required).
        Returns empty list if first_character is not provided or empty.
        """
        # Require first_character parameter
        first_character = request.query_params.get("first_character", None)

        # If not provided or empty, return empty list
        if not first_character or not first_character.strip():
            return Response([])

        # Normalize to lowercase for letters
        first_character = (
            first_character.lower() if first_character.isalpha() else first_character
        )

        # Filter and return results
        queryset = ArchiveRecord.objects.filter(
            first_character=first_character
        ).order_by("sort_name")

        serializer = ArchiveRecordSerializer(queryset, many=True)
        return Response(serializer.data)

    def characters_view(self, request):
        """
        Return available characters that have records.
        GET /api/v2/archive_records/characters/

        Returns: {"characters": ["0", "1", ..., "9", "a", "b", ..., "z", "other"]}
        Note: 'other' represents symbols - display as '#' in UI.
        """
        characters = ArchiveRecord.get_available_letters()
        return Response({"characters": characters})

    @classmethod
    def get_urlpatterns(cls):
        """
        Returns URL patterns for the endpoint.
        """
        return [
            path("", cls.as_view({"get": "list_view"}), name="list"),
            path(
                "characters/",
                cls.as_view({"get": "characters_view"}),
                name="characters",
            ),
        ]
