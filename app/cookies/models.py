from wagtail.admin.panels import FieldPanel
from wagtail.api import APIField
from wagtail.fields import StreamField

from app.core.models import BasePageWithRequiredIntro

from .blocks import CookieDetailsStreamBlock


class CookiesPage(BasePageWithRequiredIntro):
    max_count = 1
    subpage_types = ["cookies.CookieDetailsPage"]


class CookieDetailsPage(BasePageWithRequiredIntro):
    max_count = 1
    parent_page_types = ["cookies.CookiesPage"]
    subpage_types = []

    body = StreamField(CookieDetailsStreamBlock, blank=True, null=True)

    content_panels = BasePageWithRequiredIntro.content_panels + [
        FieldPanel("body"),
    ]

    class Meta:
        verbose_name = "Cookie details page"
        verbose_name_plural = "Cookie details pages"

    api_fields = BasePageWithRequiredIntro.api_fields + [APIField("body")]
