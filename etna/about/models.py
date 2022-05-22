from wagtail.admin.edit_handlers import StreamFieldPanel
from wagtail.core.fields import StreamField

from etna.core.models import BasePage

from .blocks import AboutPageStreamBlock


class AboutPage(BasePage):
    """About Page"""

    body = StreamField(AboutPageStreamBlock, blank=True, null=True)
    content_panels = BasePage.content_panels + [
        StreamFieldPanel("body"),
    ]
