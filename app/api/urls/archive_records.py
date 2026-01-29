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
    - /api/v2/archive_records/?first_character=0-9  (digits and special chars)

    Returns all matching records (no pagination).
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

        queryset = ArchiveRecord.get_records_for_letter(first_character)

        serializer = ArchiveRecordSerializer(queryset, many=True)
        return Response(serializer.data)

    def characters_view(self, request):
        """
        Return available characters that have records.
        GET /api/v2/archive_records/characters/

        Returns: {"characters": ["a", "b", ..., "z", "0-9"]}
        Note: '0-9' represents digits and special characters combined.
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
