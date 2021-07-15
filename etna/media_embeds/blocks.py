from django.conf import settings
from wagtail.core import blocks


class MediaEmbedAudioBlock(blocks.StructBlock):
    heading = blocks.CharBlock(required=True, max_length=100)
    datetime = blocks.DateTimeBlock(required=False)
    description = blocks.RichTextBlock(required=False, features=settings.INLINE_RICH_TEXT_FEATURES)
    transcript = blocks.RichTextBlock(required=False, features=settings.INLINE_RICH_TEXT_FEATURES)
    # ToDo: Add media file link field

    class Meta:
        icon = 'fa-headphones'
        label = 'Audio media embed'
        template = 'media_embeds/blocks/media-embed--audio.html'


class MediaEmbedVideoBlock(blocks.StructBlock):
    heading = blocks.CharBlock(required=True, max_length=100)
    datetime = blocks.DateTimeBlock(required=False)
    description = blocks.RichTextBlock(required=False, features=settings.INLINE_RICH_TEXT_FEATURES)
    transcript = blocks.RichTextBlock(required=False, features=settings.INLINE_RICH_TEXT_FEATURES)
    # ToDo: Add media file link field

    class Meta:
        icon = 'fa-video-camera'
        label = 'Video media embed'
        template = 'media_embeds/blocks/media-embed--video.html'
