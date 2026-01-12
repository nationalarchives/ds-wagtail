from app.core.blocks import FeaturedExternalLinkBlock, FeaturedPageBlock
from app.core.models import BasePageWithRequiredIntro, HeroImageMixin
from django.conf import settings
from django.db import models
from modelcluster.fields import ParentalKey
from wagtail.admin.panels import FieldPanel, InlinePanel
from wagtail.api import APIField
from wagtail.fields import RichTextField, StreamField
from wagtail.models import Page


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
    primary_promo = secondary_promos = StreamField(
        [
            ("featured_page", FeaturedPageBlock()),
            ("featured_external_link", FeaturedExternalLinkBlock()),
        ],
        blank=True,
        max_num=1,
        verbose_name="Primary promo link",
    )

    secondary_promos = secondary_promos = StreamField(
        [
            ("featured_page", FeaturedPageBlock()),
            ("featured_external_link", FeaturedExternalLinkBlock()),
        ],
        blank=True,
        verbose_name="Secondary promo links",
    )

    content_panels = (
        BasePageWithRequiredIntro.content_panels
        + HeroImageMixin.content_panels
        + [
            FieldPanel("primary_promo"),
            FieldPanel("secondary_promos"),
        ]
    )

    settings_panels = BasePageWithRequiredIntro.settings_panels + [
        InlinePanel("mourning", label="Mourning Notice", max_num=1),
    ]

    api_fields = (
        BasePageWithRequiredIntro.api_fields
        + HeroImageMixin.api_fields
        + [
            APIField("primary_promo"),
            APIField("secondary_promos"),
        ]
    )

    max_count = 1
