from django.core.exceptions import ValidationError
from django.db import models
from rest_framework import serializers
from wagtail import blocks
from wagtail.admin.panels import FieldPanel, MultiFieldPanel, TitleFieldPanel
from wagtail.api import APIField
from wagtail.api.v2.serializers import StreamField as StreamFieldSerializer
from wagtail.fields import StreamField
from wagtail.snippets.models import register_snippet

from app.core.blocks import (
    SimplifiedAccordionBlock,
)
from app.core.serializers import ImageSerializer


@register_snippet
class Location(models.Model):
    """
    A model representing a location (physical or online).
    """

    space_name = models.CharField(max_length=255, verbose_name="Space name")

    at_tna = models.BooleanField(
        default=False,
        verbose_name="at The National Archives",
        help_text="Check if this venue is at The National Archives.",
    )

    online = models.BooleanField(
        default=False,
        verbose_name="online venue",
        help_text="Check if this is an online venue.",
    )

    # Address fields
    address_line_1 = models.CharField(
        max_length=255,
        blank=True,
        null=True,
        verbose_name="first line of address",
        help_text="First line of address for the location, if applicable.",
    )

    address_line_2 = models.CharField(
        max_length=255,
        blank=True,
        null=True,
        verbose_name="second line of address",
        help_text="Second line of address for the location, if applicable.",
    )

    postcode = models.CharField(
        max_length=20,
        blank=True,
        null=True,
        verbose_name="postcode",
        help_text="Postcode for the location, if applicable.",
    )

    online_detail = models.CharField(
        max_length=255,
        blank=True,
        null=True,
        verbose_name="online detail",
        help_text="Additional detail for online venues, if applicable.",
    )

    image = models.ForeignKey(
        "images.CustomImage",
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="+",
        verbose_name="Image",
        help_text="An image representing the location, if applicable.",
    )

    details_title = models.CharField(
        max_length=100,
        blank=True,
        help_text="Leave blank to default to 'Plan your visit'.",
    )

    details = StreamField(
        [("details", blocks.ListBlock(SimplifiedAccordionBlock()))],
        blank=True,
        max_num=1,
    )

    venue_link = models.URLField(
        blank=True,
        null=True,
        verbose_name="Venue link",
        help_text="A link to the venue's website or visit us page.",
    )

    venue_link_text = models.CharField(
        max_length=50,
        blank=True,
        null=True,
        verbose_name="Venue link text",
        help_text="Text to display for the venue link, if applicable.",
    )

    panels = [
        TitleFieldPanel("space_name", placeholder="Space name"),
        MultiFieldPanel(
            [
                FieldPanel("online"),
                FieldPanel("online_detail"),
            ],
            heading="Online Venue Details",
            help_text="Fill in these details for online venues only.",
        ),
        MultiFieldPanel(
            [
                FieldPanel("at_tna"),
                FieldPanel("address_line_1"),
                FieldPanel("address_line_2"),
                FieldPanel("postcode"),
            ],
            heading="Physical address",
            help_text="Fill in these details for physical venues only.",
        ),
        MultiFieldPanel(
            [
                FieldPanel("image"),
                FieldPanel("details"),
                FieldPanel("venue_link"),
                FieldPanel("venue_link_text"),
            ],
            heading="Key details",
        ),
    ]

    api_fields = [
        APIField("space_name"),
        APIField("at_tna"),
        APIField("online"),
        APIField("online_detail"),
        APIField("address_line_1"),
        APIField("address_line_2"),
        APIField("postcode"),
        APIField("full_address"),
        APIField("image", serializer=ImageSerializer()),
        APIField("details"),
        APIField("venue_link"),
        APIField("venue_link_text"),
    ]

    def clean(self):
        if self.online and (
            self.at_tna or self.address_line_1 or self.address_line_2 or self.postcode
        ):
            raise ValidationError("A location cannot be online and have an address.")
        if self.at_tna and (
            self.address_line_1 or self.address_line_2 or self.postcode
        ):
            raise ValidationError(
                "Please do not enter an address for a location if it is at The National Archives."
            )
        if (
            not self.online
            and not self.at_tna
            and not (self.address_line_1 or self.address_line_2 or self.postcode)
        ):
            raise ValidationError(
                "Please enter an address. A location must either be at The National Archives, online, or have a physical address."
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

        return ", ".join(
            value
            for value in [self.address_line_1, self.address_line_2, self.postcode]
            if value
        )

    def __str__(self):
        if self.at_tna:
            return f"{self.space_name} - The National Archives"
        if self.online:
            return f"{self.space_name} - Online"
        if self.address_line_1:
            return f"{self.space_name} - {self.address_line_1}"
        return f"{self.space_name}"

    class Meta:
        verbose_name = "Location"
        verbose_name_plural = "Locations"


class LocationSerializer(serializers.Serializer):
    """
    Serializer for the Location model.
    """

    def to_representation(self, instance):
        if instance:
            representation = {
                "space_name": instance.space_name,
                "at_tna": instance.at_tna,
                "online": instance.online,
                "online_detail": instance.online_detail,
                "address_line_1": instance.address_line_1,
                "address_line_2": instance.address_line_2,
                "postcode": instance.postcode,
                "full_address": instance.full_address,
                "details": StreamFieldSerializer().to_representation(instance.details),
                "image": ImageSerializer().to_representation(instance.image),
                "venue_link": instance.venue_link,
                "venue_link_text": instance.venue_link_text,
            }
            if instance.at_tna:
                representation["address_line_1"] = "The National Archives"
                representation["address_line_2"] = "Kew, Richmond"
                representation["postcode"] = "TW9 4DU"
            return representation
        return None
