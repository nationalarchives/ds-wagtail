from wagtail.admin.panels import FieldPanel
from wagtail.api import APIField
from wagtail.fields import StreamField

from etna.core.models import BasePageWithIntro

from .blocks import HomePageStreamBlock


class HomePage(BasePageWithIntro):
    body = StreamField(HomePageStreamBlock, blank=True, null=True)

    content_panels = BasePageWithIntro.content_panels + [
        FieldPanel("body"),
    ]

    # DataLayerMixin overrides
    gtm_content_group = "Homepage"

    api_fields = BasePageWithIntro.api_fields + [
        APIField("body"),
    ]
