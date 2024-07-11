import re

from django.core.exceptions import ValidationError

from wagtail import blocks

from .image import APIImageChooserBlock


class YouTubeBlock(blocks.StructBlock):
    title = blocks.CharBlock(required=True, max_length=100, label="Title")
    video_id = blocks.CharBlock(required=True, max_length=11, label="YouTube Video ID")
    preview_image = APIImageChooserBlock(
        rendition_size="max-640x360", required=False, label="Preview Image"
    )

    def clean(self, value):
        if video_id := value.get("video_id"):
            if not re.match(r"^[a-zA-Z0-9_-]{11}$", video_id):
                raise ValidationError("Invalid YouTube Video ID")

        return super().clean(value)

    class Meta:
        label = "YouTube Video"
        icon = "media"
