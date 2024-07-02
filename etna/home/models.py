from wagtail.admin.panels import FieldPanel
from wagtail.api import APIField
from wagtail.fields import StreamField

from etna.alerts.models import AlertMixin
from etna.core.models import BasePageWithIntro

from .blocks import HomePageStreamBlock


class HomePage(AlertMixin, BasePageWithIntro):
    body = StreamField(HomePageStreamBlock, blank=True, null=True)

    content_panels = BasePageWithIntro.content_panels + [
        FieldPanel("body"),
    ]

    settings_panels = BasePageWithIntro.settings_panels + AlertMixin.settings_panels

    # DataLayerMixin overrides
    gtm_content_group = "Homepage"

    api_fields = [
        APIField("intro"),
        APIField("body"),
    ]
