from wagtail.admin.edit_handlers import StreamFieldPanel
from wagtail.core.fields import StreamField
from wagtail.core.models import Page

from taggit.models import ItemBase, TagBase

from etna.core.models import BasePage, ContentWarningMixin

from ..heroes.models import HeroImageMixin
from ..teasers.models import TeaserImageMixin
from .blocks import AboutPageStreamBlock


class AboutPage(BasePage):
    """About Page"""

    body = StreamField(AboutPageStreamBlock, blank=True, null=True)
    content_panels = BasePage.content_panels + [
        StreamFieldPanel("body"),
    ]
