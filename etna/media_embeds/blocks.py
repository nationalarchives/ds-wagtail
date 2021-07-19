from django.conf import settings
from django.forms.utils import ErrorList
from django.core.exceptions import ValidationError

from wagtail.core import blocks

import re


class MediaEmbedAudioBlock(blocks.StructBlock):
    heading = blocks.CharBlock(required=True, max_length=100)
    date = blocks.DateBlock(required=False)
    description = blocks.RichTextBlock(required=False, features=settings.INLINE_RICH_TEXT_FEATURES)
    media_file_url = blocks.URLBlock(required=True, label='Audio file URL')
    transcript = blocks.RichTextBlock(required=False, features=settings.INLINE_RICH_TEXT_FEATURES)

    def clean(self, value):
        errors = {}

        # Perform a rudimentary check for appropriate file extension in media_file_url field.
        if value.get('media_file_url'):
            if not re.search('\.mp3$', value.get('media_file_url')):
                errors['media_file_url'] = ErrorList(['Media file url field must contain a link to an audio file (.mp3)'])

            if errors:
                raise ValidationError('Validation error in Media Embed Audio Block', params=errors)

        return super().clean(value)

    class Meta:
        icon = 'fa-headphones'
        label = 'Audio media embed'
        template = 'media_embeds/blocks/media-embed--audio.html'


class MediaEmbedVideoBlock(blocks.StructBlock):
    heading = blocks.CharBlock(required=True, max_length=100)
    date = blocks.DateBlock(required=False)
    description = blocks.RichTextBlock(required=False, features=settings.INLINE_RICH_TEXT_FEATURES)
    media_file_url = blocks.URLBlock(required=True, label='Video file URL')
    transcript = blocks.RichTextBlock(required=False, features=settings.INLINE_RICH_TEXT_FEATURES)

    def clean(self, value):
        errors = {}

        # Perform a rudimentary check for appropriate file extension in media_file_url field.
        if value.get('media_file_url'):
            if not re.search('\.mp4$', value.get('media_file_url')):
                errors['media_file_url'] = ErrorList(['Media file url field must contain a link to a video file (.mp4)'])

            if errors:
                raise ValidationError('Validation error in Media Embed Video Block', params=errors)

        return super().clean(value)

    class Meta:
        icon = 'fa-video-camera'
        label = 'Video media embed'
        template = 'media_embeds/blocks/media-embed--video.html'
