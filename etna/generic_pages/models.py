from django.conf import settings
from django.utils.translation import gettext_lazy as _

from wagtail.admin.panels import FieldPanel
from wagtail.api import APIField
from wagtail.fields import RichTextField, StreamField

from etna.core.models import BasePage
from etna.core.serializers import RichTextSerializer

from .blocks import GeneralPageStreamBlock


class GeneralPage(BasePage):
    intro = RichTextField(
        verbose_name=_("introductory text"),
        help_text=_(
            "1-2 sentences introducing the subject of the page, and explaining why a user should read on."
        ),
        features=settings.INLINE_RICH_TEXT_FEATURES,
        max_length=300,
        blank=True,
        null=True,
    )

    body = StreamField(GeneralPageStreamBlock, blank=True, null=True)

    content_panels = BasePage.content_panels + [
        FieldPanel("intro"),
        FieldPanel("body"),
    ]

    api_fields = BasePage.api_fields + [
        APIField("intro", serializer=RichTextSerializer()),
        APIField("body"),
    ]


class HubPage(BasePage):

    content_panels = BasePage.content_panels

    api_fields = BasePage.api_fields
