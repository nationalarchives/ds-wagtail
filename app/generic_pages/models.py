from django.core.exceptions import ValidationError
from django.db import models
from django.utils.translation import gettext_lazy as _
from modelcluster.fields import ParentalKey
from rest_framework import serializers
from wagtail.admin.panels import FieldPanel, InlinePanel, MultiFieldPanel
from wagtail.api import APIField
from wagtail.fields import StreamField
from wagtail.images import get_image_model_string
from wagtail.models import Orderable

from app.core.models import BasePageWithIntro, HeroImageMixin, SidebarMixin
from app.core.serializers import (
    DefaultPageSerializer,
    ImageSerializer,
)

from .blocks import GeneralPageStreamBlock, HubPageStreamBlock


class GeneralPage(SidebarMixin, HeroImageMixin, BasePageWithIntro):
    body = StreamField(GeneralPageStreamBlock, blank=True, null=True)

    content_panels = (
        BasePageWithIntro.content_panels
        + HeroImageMixin.content_panels
        + [
            FieldPanel("body"),
        ]
    )

    settings_panels = BasePageWithIntro.settings_panels + SidebarMixin.settings_panels

    api_fields = (
        BasePageWithIntro.api_fields
        + SidebarMixin.api_fields
        + HeroImageMixin.api_fields
        + [
            APIField("body"),
        ]
    )


class LinkItem(Orderable):
    page = ParentalKey("HubPage", related_name="links")

    title = models.CharField(max_length=255, null=True, blank=True)
    image = models.ForeignKey(
        get_image_model_string(),
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="+",
    )
    description = models.CharField(max_length=255, null=True, blank=True)
    url = models.URLField(verbose_name="URL", blank=True, null=True)

    internal_page = models.ForeignKey(
        "wagtailcore.Page",
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="+",
    )

    panels = [
        FieldPanel("internal_page"),
        MultiFieldPanel(
            [
                FieldPanel("title"),
                FieldPanel("image"),
                FieldPanel("description"),
                FieldPanel("url"),
            ],
            heading="External page details",
        ),
    ]

    def clean(self) -> None:
        if not self.internal_page and not (
            self.url and self.title and self.description
        ):
            raise ValidationError(
                {
                    "internal_page": "You must select an internal page or provide external page details."
                }
            )
        if self.internal_page and (
            self.url or self.title or self.description or self.image
        ):
            raise ValidationError(
                {
                    "internal_page": "You can only select an internal page or provide external page details, not both."
                }
            )
        if (
            self.page.plain_cards_list is False
            and not self.image
            and not self.internal_page
        ):
            raise ValidationError(
                {"image": "You must provide an image if using an external page."}
            )
        return super().clean()

    api_fields = [
        APIField("title"),
        APIField("image"),
        APIField("description"),
        APIField("url"),
        APIField("internal_page"),
    ]


class LinkItemSerializer(serializers.Serializer):
    def to_representation(self, instance):
        if instance.internal_page:
            return DefaultPageSerializer().to_representation(instance.internal_page)
        else:
            return {
                "title": instance.title,
                "teaser_image": ImageSerializer().to_representation(instance.image),
                "teaser_text": instance.description,
                "url": instance.url,
                "full_url": instance.url,
                "type_label": "External",
            }


class HubPage(HeroImageMixin, BasePageWithIntro):
    body = StreamField(HubPageStreamBlock, blank=True, null=True)

    plain_cards_list = models.BooleanField(
        default=False,
        help_text=_(
            "If checked, the links will be displayed as a list of plain cards, without images."
        ),
    )

    content_panels = (
        BasePageWithIntro.content_panels
        + HeroImageMixin.content_panels
        + [
            FieldPanel("body"),
            FieldPanel("plain_cards_list"),
            InlinePanel("links", label="Links"),
        ]
    )

    api_fields = (
        BasePageWithIntro.api_fields
        + HeroImageMixin.api_fields
        + [
            APIField("body"),
            APIField("plain_cards_list"),
            APIField("links", serializer=LinkItemSerializer(many=True)),
        ]
    )
