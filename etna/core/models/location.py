from django.core.exceptions import ValidationError
from django.db import models
from django.utils.translation import gettext_lazy as _
from rest_framework import serializers
from wagtail import blocks
from wagtail.admin.panels import FieldPanel, MultiFieldPanel, TitleFieldPanel
from wagtail.api import APIField
from wagtail.api.v2.serializers import StreamField as StreamFieldSerializer
from wagtail.fields import StreamField
from wagtail.snippets.models import register_snippet

from etna.core.blocks import (
    SimplifiedAccordionBlock,
)


@register_snippet
class Location(models.Model):
    """
    A model representing a location (physical or online).
    """

    space_name = models.CharField(max_length=255, verbose_name=_("Space name"))

    at_tna = models.BooleanField(
        default=False,
        verbose_name=_("at The National Archives"),
        help_text=_("Check if this venue is at The National Archives."),
    )

    online = models.BooleanField(
        default=False,
        verbose_name=_("online venue"),
        help_text=_("Check if this is an online venue."),
    )

    # Address fields
    first_line = models.CharField(
        max_length=255,
        blank=True,
        null=True,
        verbose_name=_("first line of address"),
        help_text=_("First line of address for the location, if applicable."),
    )

    second_line = models.CharField(
        max_length=255,
        blank=True,
        null=True,
        verbose_name=_("second line of address"),
        help_text=_("Second line of address for the location, if applicable."),
    )

    postcode = models.CharField(
        max_length=20,
        blank=True,
        null=True,
        verbose_name=_("postcode"),
        help_text=_("Postcode for the location, if applicable."),
    )

    online_detail = models.CharField(
        max_length=255,
        blank=True,
        null=True,
        verbose_name=_("online detail"),
        help_text=_("Additional detail for online venues, if applicable."),
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
        TitleFieldPanel("space_name", placeholder="Space name"),
        MultiFieldPanel(
            [
                FieldPanel("online"),
                FieldPanel("online_detail"),
            ],
            heading=_("Online Venue Details"),
            help_text=_("Fill in these details for online venues only."),
        ),
        MultiFieldPanel(
            [
                FieldPanel("at_tna"),
                FieldPanel("first_line"),
                FieldPanel("second_line"),
                FieldPanel("postcode"),
            ],
            heading=_("Physical address"),
            help_text=_("Fill in these details for physical venues only."),
        ),
        MultiFieldPanel(
            [
                FieldPanel("details_title"),
                FieldPanel("details"),
            ],
            heading=_("Key details"),
        ),
    ]

    api_fields = [
        APIField("space_name"),
        APIField("at_tna"),
        APIField("online"),
        APIField("first_line"),
        APIField("second_line"),
        APIField("postcode"),
        APIField("full_address"),
        APIField("details_title"),
        APIField("details"),
    ]

    def clean(self):
        if self.online and (
            self.at_tna or self.first_line or self.second_line or self.postcode
        ):
            raise ValidationError("A location cannot be online and have an address.")
        if self.at_tna and (self.first_line or self.second_line or self.postcode):
            raise ValidationError(
                "Please do not enter an address for a location if it is at The National Archives."
            )
        if (
            not self.online
            and not self.at_tna
            and not (self.first_line or self.second_line or self.postcode)
        ):
            raise ValidationError(
                "Please enter an address for a location that is not online or at The National Archives."
            )
        if self.online_detail and not self.online:
            raise ValidationError(
                "Online detail can only be provided for online venues."
            )
        return super().clean()

    @property
    def full_address(self):
        """
        Returns the full address of the location.
        """
        if self.at_tna:
            return "The National Archives, Kew, Richmond, TW9 4DU"
        if self.online:
            return f"Online, {self.space_name}"

        return (
            f"{self.first_line}, {self.second_line}, {self.postcode}"
            if self.first_line or self.second_line or self.postcode
            else ""
        )

    def __str__(self):
        if self.at_tna:
            return f"{self.space_name} - The National Archives"
        elif self.online:
            return f"{self.space_name} - Online"
        elif self.first_line:
            return f"{self.space_name} - {self.first_line}"
        return f"{self.space_name}"

    class Meta:
        verbose_name = _("Location")
        verbose_name_plural = _("Locations")


class LocationSerializer(serializers.ModelSerializer):
    """
    Serializer for the Location model.
    """

    details = StreamFieldSerializer()

    class Meta:
        model = Location
        fields = (
            "space_name",
            "at_tna",
            "online",
            "first_line",
            "second_line",
            "postcode",
            "full_address",
            "details_title",
            "details",
        )
