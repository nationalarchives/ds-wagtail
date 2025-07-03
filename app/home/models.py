from django.conf import settings
from django.db import models
from modelcluster.fields import ParentalKey
from wagtail.admin.panels import FieldPanel, InlinePanel
from wagtail.api import APIField
from wagtail.fields import RichTextField, StreamField
from wagtail.models import Page

from app.core.models import BasePageWithRequiredIntro

from .blocks import HomePageStreamBlock


class MourningNotice(models.Model):
    """
    A model to hold mourning notice information.
    """

    page = ParentalKey(Page, on_delete=models.CASCADE, related_name="mourning")
    title = models.CharField(max_length=255)
    message = RichTextField(features=settings.INLINE_RICH_TEXT_FEATURES)

    panels = [
        FieldPanel("title"),
        FieldPanel("message"),
    ]


class HomePage(BasePageWithRequiredIntro):
    body = StreamField(HomePageStreamBlock, blank=True, null=True)

    content_panels = BasePageWithRequiredIntro.content_panels + [
        FieldPanel("body"),
    ]

    settings_panels = BasePageWithRequiredIntro.settings_panels + [
        InlinePanel("mourning", label="Mourning Notice", max_num=1),
    ]

    # DataLayerMixin overrides
    gtm_content_group = "Homepage"

    api_fields = BasePageWithRequiredIntro.api_fields + [
        APIField("body"),
    ]

    max_count = 1
