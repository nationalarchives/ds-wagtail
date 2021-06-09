from django.db import models
from django.conf import settings

from wagtail.contrib.settings.models import BaseSetting, register_setting
from wagtail.admin.edit_handlers import MultiFieldPanel, FieldPanel


@register_setting(icon='link', order=settings.MENU_ORDER.SOCIAL_MEDIA)
class SocialLinks(BaseSetting):
    twitter = models.URLField(
        help_text='Your Twitter page URL',
        blank=True
    )
    youtube = models.URLField(
        help_text='Your YouTube channel or user account URL',
        blank=True
    )
    flickr = models.URLField(
        help_text='Your Flickr page URL',
        blank=True
    )
    facebook = models.URLField(
        help_text='Your Facebook page URL',
        blank=True
    )
    instagram = models.URLField(
        help_text='Your Instagram page URL',
        blank=True
    )
    rss = models.URLField(
        help_text='Your RSS feed URL',
        blank=True
    )

    panels = [
        FieldPanel('twitter'),
        FieldPanel('youtube'),
        FieldPanel('flickr'),
        FieldPanel('facebook'),
        FieldPanel('instagram'),
        FieldPanel('rss'),
    ]

    class Meta:
        verbose_name = 'Social media links'
