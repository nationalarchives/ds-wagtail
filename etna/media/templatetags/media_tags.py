from django import template

from ..blocks import MediaBlock


register = template.Library()


@register.inclusion_tag("media/blocks/media-block--audio.html")
def audio(media):
    return {
            "value": media,
            "src": media.sources[0]["src"],
            "type": media.sources[0]["type"],
        }


@register.inclusion_tag("media/blocks/media-block--video.html")
def video(media):
    return {
            "value": media,
            "src": media.sources[0]["src"],
            "type": media.sources[0]["type"],
        }
