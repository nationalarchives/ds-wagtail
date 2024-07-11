from wagtail import blocks

from .image import APIImageChooserBlock


class YouTubeBlock(blocks.StructBlock):
    title = blocks.CharBlock(required=True, max_length=100, label="Title")
    video_id = blocks.CharBlock(required=True, max_length=100, label="YouTube Video ID")
    preview_image = APIImageChooserBlock(
        rendition_size="max-640x360", required=False, label="Preview Image"
    )

    class Meta:
        label = "YouTube Video"
        icon = "media"
