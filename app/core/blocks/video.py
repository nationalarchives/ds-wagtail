from django.core.validators import RegexValidator
from wagtail import blocks

from app.media.blocks import MediaBlock

from .image import APIImageChooserBlock


class YouTubeBlock(blocks.StructBlock):
    title = blocks.CharBlock(required=True, max_length=100, label="Title")
    video_id = blocks.CharBlock(
        required=True,
        max_length=11,
        label="YouTube Video ID",
        validators=[
            RegexValidator(
                regex=r"^[a-zA-Z0-9_-]{11}$", message="Invalid YouTube Video ID"
            )
        ],
    )
    preview_image = APIImageChooserBlock(
        rendition_size="fill-640x360", required=True, label="Preview Image"
    )
    transcript = blocks.RichTextBlock(required=False, label="Transcript")
    captions_available = blocks.BooleanBlock(
        required=False,
        label="Captions available",
        help_text="Tick if the video has captions on YouTube",
    )

    class Meta:
        label = "YouTube Video"
        icon = "media"


class MixedMediaBlock(blocks.StreamBlock):
    youtube = YouTubeBlock()
    media = MediaBlock()

    class Meta:
        label = "Mixed Media"
        icon = "media"
