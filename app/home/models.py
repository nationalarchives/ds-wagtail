from django.conf import settings
from django.db import models
from modelcluster.fields import ParentalKey
from wagtail.admin.panels import FieldPanel, InlinePanel, MultiFieldPanel
from wagtail.api import APIField
from wagtail.fields import RichTextField, StreamField
from wagtail.images import get_image_model_string
from wagtail.models import Page

from app.core.blocks import FeaturedPagesBlock
from app.core.models import BasePageWithRequiredIntro, HeroImageMixin
from app.core.serializers.pages import DefaultPageSerializer


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


class HomePage(HeroImageMixin, BasePageWithRequiredIntro):
    primary_promo_title = models.CharField(max_length=255, null=True, blank=True)
    primary_promo_image = models.ForeignKey(
        get_image_model_string(),
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="+",
    )
    primary_promo_description = models.CharField(max_length=255, null=True, blank=True)
    primary_promo_chip = models.CharField(max_length=20, null=True, blank=True)
    primary_promo_url = models.URLField(verbose_name="URL", blank=True, null=True)
    primary_promo_internal_page = models.ForeignKey(
        "wagtailcore.Page",
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="+",
    )

    secondary_promos = StreamField(
        [("secondary_promos", FeaturedPagesBlock())],
        blank=True,
        max_num=1,
        verbose_name="Secondary promo links",
    )

    content_panels = BasePageWithRequiredIntro.content_panels + [
        MultiFieldPanel(
            [
                FieldPanel("primary_promo_internal_page"),
                FieldPanel("primary_promo_title"),
                FieldPanel("primary_promo_image"),
                FieldPanel("primary_promo_description"),
                FieldPanel("primary_promo_chip"),
                FieldPanel("primary_promo_url"),
            ],
            heading="Primary promo link",
        ),
        FieldPanel("secondary_promos"),
    ]

    settings_panels = BasePageWithRequiredIntro.settings_panels + [
        InlinePanel("mourning", label="Mourning Notice", max_num=1),
    ]

    api_fields = BasePageWithRequiredIntro.api_fields + [
        APIField("primary_promo_title"),
        APIField("primary_promo_image"),
        APIField("primary_promo_description"),
        APIField("primary_promo_chip"),
        APIField("primary_promo_url"),
        APIField("primary_promo_internal_page", serializer=DefaultPageSerializer()),
        APIField("secondary_promos"),
    ]

    max_count = 1
