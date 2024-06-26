from wagtail.admin.panels import FieldPanel
from wagtail.fields import StreamField

from etna.core.models import BasePage

from .blocks import GeneralPageStreamBlock


class GeneralPage(BasePage):
    body = StreamField(GeneralPageStreamBlock, blank=True, null=True)

    content_panels = BasePage.content_panels + [
        FieldPanel("body"),
    ]

    api_fields = BasePage.api_fields + ["body"]


class HubPage(BasePage):

    content_panels = BasePage.content_panels

    api_fields = BasePage.api_fields
