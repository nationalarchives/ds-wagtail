from django.conf import settings
from django.db import models
from django.utils.translation import gettext_lazy as _
from wagtail import blocks
from wagtail.admin.panels import (
    FieldPanel,
    TitleFieldPanel,
)
from wagtail.api import APIField
from wagtail.fields import RichTextField, StreamField
from wagtail.snippets.models import register_snippet

from etna.core.blocks import (
    SimplifiedAccordionBlock,
)
from etna.core.serializers import DefaultPageSerializer, RichTextSerializer

@register_snippet
class Location(models.Model):
    """
    A model representing a location (physical or online).
    """
    space_name = models.CharField(max_length=255, verbose_name=_("Space name"))
    address = RichTextField(
        verbose_name=_("location address"),
        null=True,
        blank=True,
        help_text=_("Leave blank to default to TNA address."),
        features=["link"],
    )
    details_title = models.CharField(
        max_length=100,
        blank=True,
        help_text=_("Leave blank to default to 'Plan your visit'."),
    )
    details = StreamField(
        [("details", blocks.ListBlock(SimplifiedAccordionBlock()))],
        blank=True,
        max_num=1,
    )

    panels = [
        TitleFieldPanel("space_name"),
        FieldPanel("address"),
        FieldPanel("details"),
    ]

    api_fields = [
        APIField("space_name"),
        APIField("address", serializer=RichTextSerializer()),
        APIField("details"),
    ]

    def __str__(self):
        return f"{self.space_name}"

    class Meta:
        verbose_name = _("Location")
        verbose_name_plural = _("Locations")
