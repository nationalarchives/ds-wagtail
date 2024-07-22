from wagtail.admin.panels import FieldPanel
from wagtail.api import APIField
from wagtail.fields import StreamField

from etna.core.models import BasePageWithRequiredIntro

from .blocks import HomePageStreamBlock


class HomePage(BasePageWithRequiredIntro):
    body = StreamField(HomePageStreamBlock, blank=True, null=True)

    content_panels = BasePageWithRequiredIntro.content_panels + [
        FieldPanel("body"),
    ]

    # DataLayerMixin overrides
    gtm_content_group = "Homepage"

    api_fields = BasePageWithRequiredIntro.api_fields + [
        APIField("body"),
    ]
