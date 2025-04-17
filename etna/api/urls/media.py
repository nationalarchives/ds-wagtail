from wagtailmedia.api.views import MediaAPIViewSet


class CustomMediaAPIViewSet(MediaAPIViewSet):
    body_fields = MediaAPIViewSet.body_fields + [
        "title",
        "file",
        "tags",
        "date",
        "created_at",
        "duration",
        "subtitles_file",
        "subtitles_file_full_url",
        "chapters_file",
        "chapters_file_full_url",
    ]
