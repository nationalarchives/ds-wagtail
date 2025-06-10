from wagtail.rich_text import expand_db_html
from wagtailmedia.api.serializers import MediaItemSerializer
from wagtailmedia.api.views import MediaAPIViewSet


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
        return super().to_representation(instance) | {
            "chapters": sorted(chapters, key=lambda x: x["time"]),
            "subtitles_file": instance.subtitles_file_url,
            "subtitles_file_full_url": instance.subtitles_file_full_url,
            "chapters_file": instance.chapters_file_url,
            "chapters_file_full_url": instance.chapters_file_full_url,
        }


class CustomMediaAPIViewSet(MediaAPIViewSet):
    base_serializer_class = CustomMediaItemSerializer
    body_fields = MediaAPIViewSet.body_fields + [
        "uuid",
        "title",
        "file",
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
