from wagtail.admin.panels import FieldPanel
from wagtail.api import APIField
from wagtail.fields import StreamField

from etna.alerts.models import AlertMixin
from etna.core.models import BasePageWithRequiredIntro

from .blocks import HomePageStreamBlock


class HomePage(AlertMixin, BasePageWithRequiredIntro):
    body = StreamField(HomePageStreamBlock, blank=True, null=True)

    content_panels = BasePageWithRequiredIntro.content_panels + [
        FieldPanel("body"),
    ]

    settings_panels = (
        BasePageWithRequiredIntro.settings_panels + AlertMixin.settings_panels
    )

    # DataLayerMixin overrides
    gtm_content_group = "Homepage"

    api_fields = [
        APIField("intro"),
        APIField("body"),
    ]
