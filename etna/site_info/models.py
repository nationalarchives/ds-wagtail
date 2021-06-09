from django.db import models
from wagtail.contrib.settings.models import BaseSetting, register_setting
from wagtail.admin.edit_handlers import MultiFieldPanel, FieldPanel


@register_setting
class SiteInformation(BaseSetting):
    site_name = models.CharField(
        max_length=100,
        blank=True
    )
    site_address = models.CharField(
        max_length=100,
        blank=True
    )

    panels = [
        MultiFieldPanel([
            FieldPanel('site_name'),
            FieldPanel('site_address'),
        ],
        heading="Site information")
    ]

    class Meta:
        verbose_name = 'Site information'
