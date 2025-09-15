from django.conf import settings
from django.db import models
from modelcluster.fields import ParentalKey
from wagtail.admin.panels import FieldPanel, InlinePanel
from wagtail.api import APIField
from wagtail.fields import RichTextField, StreamField
from wagtail.models import Page

from app.core.models import BasePageWithRequiredIntro, HeroImageMixin
from app.core.blocks import FeaturedPagesBlock

from .blocks import FeaturedItemBlock


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


# class HomePageLinkItem(Orderable):
#     page = ParentalKey("HomePage", related_name="secondary_promos")

#     title = models.CharField(max_length=255, null=True, blank=True)
#     image = models.ForeignKey(
#         get_image_model_string(),
#         null=True,
#         blank=True,
#         on_delete=models.SET_NULL,
#         related_name="+",
#     )
#     description = models.CharField(max_length=255, null=True, blank=True)
#     chip = models.CharField(max_length=20, null=True, blank=True)
#     url = models.URLField(verbose_name="URL", blank=True, null=True)

#     internal_page = models.ForeignKey(
#         "wagtailcore.Page",
#         null=True,
#         blank=True,
#         on_delete=models.SET_NULL,
#         related_name="+",
#     )

#     panels = [
#         FieldPanel("internal_page"),
#         MultiFieldPanel(
#             [
#                 FieldPanel("title"),
#                 FieldPanel("image"),
#                 FieldPanel("description"),
#                 FieldPanel("chip"),
#                 FieldPanel("url"),
#             ],
#             heading="External page details",
#         ),
#     ]

#     def clean(self) -> None:
#         if not self.internal_page and not (
#             self.url and self.title and self.description and self.chip and self.image
#         ):
#             raise ValidationError(
#                 {
#                     "internal_page": "You must select an internal page or provide external page details."
#                 }
#             )
#         if self.internal_page and (
#             self.url
#             or self.title
#             or self.description
#             or self.image
#             or self.chip
#             or self.image
#         ):
#             raise ValidationError(
#                 {
#                     "internal_page": "You can only select an internal page or provide external page details, not both."
#                 }
#             )
#         return super().clean()

#     api_fields = [
#         APIField("title"),
#         APIField("image"),
#         APIField("description"),
#         APIField("chip"),
#         APIField("url"),
#         APIField("internal_page"),
#     ]


class HomePage(HeroImageMixin, BasePageWithRequiredIntro):
    primary_promo = StreamField(
        [("primary_promo", FeaturedItemBlock())],
        blank=True,
        max_num=1,
        verbose_name="Primary promo link",
    )

    secondary_promos = StreamField(
        [("secondary_promos", FeaturedPagesBlock())],
        blank=True,
        max_num=1,
        verbose_name="Secondary promo links",
    )

    content_panels = BasePageWithRequiredIntro.content_panels + [
        FieldPanel("primary_promo"),
        FieldPanel("secondary_promos"),
    ]

    settings_panels = BasePageWithRequiredIntro.settings_panels + [
        InlinePanel("mourning", label="Mourning Notice", max_num=1),
    ]

    api_fields = BasePageWithRequiredIntro.api_fields + [
        APIField("body"),
    ]

    max_count = 1
