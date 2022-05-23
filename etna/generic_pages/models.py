from wagtail.admin.edit_handlers import StreamFieldPanel
from wagtail.core.fields import StreamField

from etna.core.models import BasePage

from .blocks import GeneralPageStreamBlock


class GeneralPage(BasePage):
    body = StreamField(GeneralPageStreamBlock, blank=True, null=True)
    content_panels = BasePage.content_panels + [
        StreamFieldPanel("body"),
    ]
