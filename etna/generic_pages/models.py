from etna.core.models import BasePage
from wagtail.admin.panels import FieldPanel
from wagtail.fields import StreamField

from .blocks import GeneralPageStreamBlock


class GeneralPage(BasePage):
    body = StreamField(GeneralPageStreamBlock, blank=True, null=True)
    content_panels = BasePage.content_panels + [
        FieldPanel("body"),
    ]
