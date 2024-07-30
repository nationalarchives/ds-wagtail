from django.db import models

from modelcluster.fields import ParentalKey
from wagtail.admin.panels import FieldPanel, InlinePanel
from wagtail.api import APIField
from wagtail.fields import StreamField
from wagtail.models import Page

from etna.core.models import BasePageWithRequiredIntro

from .blocks import HomePageStreamBlock


class MourningNotice(models.Model):
    """
    A model to hold mourning notice information.
    """

    page = ParentalKey(Page, on_delete=models.CASCADE, related_name="mourning_notice")
    name = models.CharField(max_length=255)
    birth_date = models.CharField()
    death_date = models.CharField()

    panels = [
        FieldPanel("name"),
        FieldPanel("birth_date"),
        FieldPanel("death_date"),
    ]

    api_fields = [
        APIField("name"),
        APIField("birth_date"),
        APIField("death_date"),
    ]


class HomePage(BasePageWithRequiredIntro):
    body = StreamField(HomePageStreamBlock, blank=True, null=True)

    content_panels = BasePageWithRequiredIntro.content_panels + [
        FieldPanel("body"),
    ]

    settings_panels = BasePageWithRequiredIntro.settings_panels + [
        InlinePanel("mourning_notice", label="Mourning Notice", max_num=1),
    ]

    # DataLayerMixin overrides
    gtm_content_group = "Homepage"

    api_fields = BasePageWithRequiredIntro.api_fields + [
        APIField("mourning_notice"),
        APIField("body"),
    ]
