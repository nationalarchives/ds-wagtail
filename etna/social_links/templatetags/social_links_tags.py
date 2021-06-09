from django import template

from ..models import SocialLinks

register = template.Library()


@register.inclusion_tag('social_links/tags/social-media-links.html')
def social_media_links():
    """
    Output social_links for any account with a URL
    """
    try:
        social_links = SocialLinks.objects.get()
    except SocialLinks.DoesNotExist:
        return {}

    return {
        "twitter_url": social_links.twitter,
        "youtube_url": social_links.youtube,
        "flickr_url": social_links.flickr,
        "facebook_url": social_links.facebook,
        "instagram_url": social_links.instagram,
        "rss_url": social_links.rss,
    }
