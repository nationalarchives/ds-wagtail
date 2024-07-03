from django.core.exceptions import ValidationError
from django.db import models

from modelcluster.fields import ParentalKey
from wagtail.admin.panels import FieldPanel, InlinePanel, MultiFieldPanel
from wagtail.api import APIField
from wagtail.fields import StreamField
from wagtail.images import get_image_model_string
from wagtail.models import Orderable

from etna.core.models import BasePage
from etna.core.serializers.pages import DefaultPageSerializer

from .blocks import GeneralPageStreamBlock


class GeneralPage(BasePage):
    body = StreamField(GeneralPageStreamBlock, blank=True, null=True)

    content_panels = BasePage.content_panels + [
        FieldPanel("body"),
    ]

    api_fields = BasePage.api_fields + [APIField("body")]


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
        if self.internal_page and (
            self.url or self.title or self.image or self.description
        ):
            raise ValidationError(
                {
                    "internal_page": "You can only select an internal page or provide external page details, not both."
                }
            )
        elif not self.internal_page and not (
            self.url and self.title and self.image and self.description
        ):
            raise ValidationError(
                {
                    "internal_page": "You must select an internal page or provide external page details."
                }
            )
        return super().clean()

    api_fields = [
        APIField("title"),
        APIField("image"),
        APIField("description"),
        APIField("url"),
        APIField("internal_page", serializer=DefaultPageSerializer()),
    ]


class HubPage(BasePage):
    content_panels = BasePage.content_panels + [
        InlinePanel("links", label="Link"),
    ]

    api_fields = BasePage.api_fields + [APIField("links")]
