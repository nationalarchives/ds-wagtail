from django import template

register = template.Library()


@register.inclusion_tag("media/blocks/media-block--audio.html")
def audio(title, media):
    """
    Inclusion tag to render a custom audio media block.

    Exposes "src" and "type" attributes for FE convenience.
    """
    return {
        "title": title,
        "value": media,
        "src": media.sources[0]["src"],
        "type": media.sources[0]["type"],
    }


@register.inclusion_tag("media/blocks/media-block--video.html")
def video(title, media):
    """
    Inclusion tag to render a custom video media block.

    Exposes "src" and "type" attributes for FE convenience.
    """
    return {
        "title": title,
        "value": media,
        "src": media.sources[0]["src"],
        "type": media.sources[0]["type"],
    }
