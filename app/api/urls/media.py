from django.conf import settings
from django.urls import path
from rest_framework.response import Response
from wagtail.rich_text import expand_db_html
from wagtailmedia.api.serializers import MediaItemSerializer
from wagtailmedia.api.views import MediaAPIViewSet

from app.api.permissions import IsAPITokenAuthenticated


class CustomMediaItemSerializer(MediaItemSerializer):
    def to_representation(self, instance):
        chapters = [
            {
                "time": int(chapter.value["time"]),
                "heading": chapter.value["heading"],
                "transcript": expand_db_html(chapter.value["transcript"].source),
            }
            for chapter in instance.chapters
        ]
        representation = super().to_representation(instance)
        representation["uuid"] = instance.uuid
        return representation | {
            "chapters": sorted(chapters, key=lambda x: x["time"]),
            "subtitles_file": instance.subtitles_file_url,
            "subtitles_file_full_url": instance.subtitles_file_full_url,
            "chapters_file": instance.chapters_file_url,
            "chapters_file_full_url": instance.chapters_file_full_url,
        }


class CustomMediaAPIViewSet(MediaAPIViewSet):
    if settings.WAGTAILAPI_AUTHENTICATION:
        permission_classes = (
            IsAPITokenAuthenticated,
        )

    lookup_field = "uuid"
    base_serializer_class = CustomMediaItemSerializer
    meta_fields = MediaAPIViewSet.meta_fields
    body_fields = MediaAPIViewSet.body_fields + [
        "uuid",
        "title",
        "url",
        "full_url",
        "audio_described_file",
        "tags",
        "thumbnail",
        "date",
        "created_at",
        "duration",
        "subtitles_file",
        "subtitles_file_full_url",
        "chapters",
        "chapters_file",
        "chapters_file_full_url",
    ]
    meta_fields.remove("download_url")
    meta_fields.remove("detail_url")

    def find_object(self, queryset, request):
        if "uuid" in request.GET:
            return queryset.get(uuid=request.GET["uuid"])

    def detail_view(self, request, uuid):
        instance = self.get_object()
        serializer = self.get_serializer(instance)
        return Response(serializer.data)

    @classmethod
    def get_urlpatterns(cls):
        return [
            path("", cls.as_view({"get": "listing_view"}), name="listing"),
            path("<str:uuid>/", cls.as_view({"get": "detail_view"}), name="detail"),
        ]
