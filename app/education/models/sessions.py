from django.core.exceptions import ValidationError
from django.db import models
from django.utils.translation import gettext_lazy as _
from modelcluster.fields import ParentalKey
from wagtail.admin.panels import (
    FieldPanel,
    InlinePanel,
    MultiFieldPanel,
    ObjectList,
    TabbedInterface,
)
from wagtail.api import APIField
from wagtail.fields import RichTextField, StreamField
from wagtail.models import Orderable

from app.core.blocks.image import (
    ImageGalleryBlock,
)
from app.core.models import (
    BasePageWithRequiredIntro,
    PublishedDateMixin,
    RequiredHeroImageMixin,
)

from ..blocks import SessionDescriptionBlock
from ..serializers import (
    KeyStageSerializer,
    ThemeSerializer,
    TimePeriodSerializer,
)
from .details import (
    BaseKeyStageTag,
    BaseThemeTag,
    BaseTimePeriodTag,
)
from .mixins import EducationTaxonomyMixin


class EducationSessionPageKeyStageTag(BaseKeyStageTag):
    page = ParentalKey(
        "education.EducationSessionPage",
        on_delete=models.CASCADE,
        related_name="education_keystage_tags",
    )


class EducationSessionPageTimePeriodTag(BaseTimePeriodTag):
    page = ParentalKey(
        "education.EducationSessionPage",
        on_delete=models.CASCADE,
        related_name="education_time_period_tags",
    )


class EducationSessionPageThemeTag(BaseThemeTag):
    page = ParentalKey(
        "education.EducationSessionPage",
        on_delete=models.CASCADE,
        related_name="education_theme_tags",
    )


class SessionLocation(Orderable):
    class LocationType(models.TextChoices):
        ONLINE = "online", _("Online")
        NATIONAL_ARCHIVES = "national_archives", _("At The National Archives")
        YOUR_SCHOOL = "your_school", _("At your school")
        CUSTOM = "custom", _("Custom venue")

    class Regions(models.TextChoices):
        SOUTH_EAST_LONDON = "south_east", "South East and London"
        SOUTH_WEST = "south_west", "South West"
        MIDLANDS = "midlands", "Midlands"
        NORTH_EAST = "north_east", "North East"
        NORTH_WEST = "north_west", "North West"

    page = ParentalKey(
        "education.EducationSessionPage",
        on_delete=models.CASCADE,
        related_name="session_locations",
    )

    location_type = models.CharField(
        max_length=32,
        choices=LocationType.choices,
        verbose_name=_("location type"),
        help_text=_("Choose a standard location or Custom venue."),
        null=True,
    )

    duration = models.CharField(
        verbose_name=_("duration"),
        help_text=_(
            "A clear description of the session duration for this location, e.g. 1 hour, 1 to 2 hours."
        ),
        blank=True,
        null=True,
        max_length=160,
    )

    region = models.CharField(
        max_length=32,
        choices=Regions.choices,
        verbose_name=_("region"),
        help_text=_("The region where the session is offered. Required for schools and custom venues."),
        null=True,
        blank=True,
    )

    venue_name = models.CharField(
        blank=True,
        null=True,
        max_length=255,
        verbose_name=_("Venue name"),
        help_text=_("Required only when location type is Custom venue."),
    )
    address_line_1 = models.CharField(
        blank=True,
        null=True,
        max_length=255,
        verbose_name=_("Address line 1"),
        help_text=_("Required only when location type is Custom venue."),
    )
    address_line_2 = models.CharField(
        blank=True,
        null=True,
        max_length=255,
        verbose_name=_("Address line 2"),
        help_text=_("Required only when location type is Custom venue."),
    )
    postcode = models.CharField(
        blank=True,
        null=True,
        max_length=20,
        verbose_name=_("Postcode"),
        help_text=_("Required only when location type is Custom venue."),
    )

    panels = [
        FieldPanel("location_type"),
        FieldPanel("duration"),
        FieldPanel("region"),
        MultiFieldPanel(
            [
                FieldPanel("venue_name"),
                FieldPanel("address_line_1"),
                FieldPanel("address_line_2"),
                FieldPanel("postcode"),
            ],
            heading=_("Custom venue address details"),
        ),
    ]

    class Meta:
        verbose_name = _("session location")
        verbose_name_plural = _("session locations")
        ordering = ["sort_order"]

    def clean(self):
        super().clean()
        errors = {}

        venue_name = (self.venue_name or "").strip()
        address_line_1 = (self.address_line_1 or "").strip()
        address_line_2 = (self.address_line_2 or "").strip()
        postcode = (self.postcode or "").strip()
        region = (self.region or "").strip()

        has_venue_details = any([venue_name, address_line_1, address_line_2, postcode])
        location_requires_region = self.location_type in [
            self.LocationType.YOUR_SCHOOL,
            self.LocationType.CUSTOM,
        ]

        if self.location_type == self.LocationType.CUSTOM:
            if not venue_name:
                errors["venue_name"] = _("Venue name is required for custom venue.")
            if not address_line_1:
                errors["address_line_1"] = _(
                    "Address line 1 is required for custom venue."
                )
            if not postcode:
                errors["postcode"] = _("Postcode is required for custom venue.")
        elif has_venue_details:
            errors["venue_name"] = _(
                "Venue details should only be provided for custom venue location type."
            )

        if location_requires_region and not region:
            errors["region"] = _(
                "Region is required for school or custom venue location types."
            )
        elif region and not location_requires_region:
            errors["region"] = _(
                "Region should only be provided for school or custom venue location types."
            )

        if errors:
            raise ValidationError(errors)
        

    @property
    def display_label(self):
        if self.location_type == self.LocationType.CUSTOM:
            if self.venue_details:
                venue_name = self.venue_details[0].value.get("venue_name")
                if venue_name:
                    return venue_name
            return self.get_location_type_display()
        return self.get_location_type_display()

    def __str__(self):
        return self.display_label


class RelatedEducationSessions(Orderable):
    """Links to take users to related education sessions"""

    page = ParentalKey(
        "education.EducationSessionPage",
        on_delete=models.CASCADE,
        related_name="related_education_sessions",
    )

    selected_page = models.ForeignKey(
        "education.EducationSessionPage",
        on_delete=models.CASCADE,
        related_name="+",
        verbose_name=_("selected page"),
    )

    class Meta:
        verbose_name = _("related education session")
        ordering = ["sort_order"]


class EducationSessionPage(
    EducationTaxonomyMixin,
    PublishedDateMixin,
    RequiredHeroImageMixin,
    BasePageWithRequiredIntro,
):
    """A page to display an education session"""

    parent_page_types = [
        "education.EducationSessionsListingPage",
    ]

    start_date = models.DateField(
        verbose_name=_("start date"),
        null=True,
        blank=True,
        help_text=_(
            "If neither start nor end date is added this will default to 'All Year'"
        ),
    )

    end_date = models.DateField(
        verbose_name=_("end date"),
        null=True,
        blank=True,
        help_text=_(
            "If neither start nor end date is added this will default to 'All Year'"
        ),
    )

    price = models.FloatField(
        null=True, blank=True, verbose_name=_("price")
    )

    price_detail = models.CharField(
        verbose_name=_("price detail"),
        help_text=_(
            "An explanation of the price. Required if price is filled in."
        ),
        blank=True,
        max_length=160,
    )

    booking_link = models.URLField(
        null=True,
        blank=True,
        help_text=_("Link to booking page"),
        verbose_name=_("Booking link"),
    )

    description = StreamField(
        [("description", SessionDescriptionBlock())],
        verbose_name=_("description"),
        blank=True,
        null=True,
        min_num=1,
    )

    curriculum_connection_description = RichTextField(
        verbose_name=_("curriculum connection description"),
        help_text=_(
            "A description of how the session connects to the curriculum. This is optional but can help teachers understand the relevance of the session to their teaching."
        ),
        blank=True,
        null=True,
    )

    highlights = StreamField(
        [("highlights", ImageGalleryBlock())],
        blank=True,
        help_text=_("Optional image gallery to show what to expect from the session."),
        max_num=1,
    )

    def clean(self):
        super().clean()

        if self.price is not None and not self.price_detail:
            raise ValidationError(
                {
                    "price_detail": _(
                        "Price detail is required when a session price is specified."
                    )
                }
            )

    content_panels = (
        BasePageWithRequiredIntro.content_panels
        + RequiredHeroImageMixin.content_panels
        + [
            MultiFieldPanel(
                [
                    FieldPanel("description"),
                    FieldPanel("curriculum_connection_description"),
                    FieldPanel("highlights"),
                ]
            ),
            InlinePanel(
                "related_education_sessions",
                heading=_("More education sessions"),
                help_text=_(
                    "Education sessions that are selected to be shown in the related education sessions section"
                ),
            ),
        ]
    )

    key_details_panels = (
        [
            MultiFieldPanel(
                [
                    FieldPanel("start_date"),
                    FieldPanel("end_date"),
                    MultiFieldPanel(
                        [
                            FieldPanel("price"),
                            FieldPanel("price_detail"),
                        ],
                        heading=_("Session price"),
                    ),
                    InlinePanel(
                        "session_locations",
                        label=_("Location"),
                        heading=_("Session locations"),
                        min_num=1,
                    ),
                    FieldPanel("booking_link"),
                ],
            ),
        ]
    )

    promote_panels = (
        BasePageWithRequiredIntro.promote_panels
        + PublishedDateMixin.promote_panels
        + EducationTaxonomyMixin.taxonomy_promote_panels()
    )

    api_fields = BasePageWithRequiredIntro.api_fields + [
        # TODO: primary tags?
        # APIField("key_stage", serializer=KeyStageSerializer()),
        # APIField("time_period", serializer=TimePeriodSerializer()),
        # APIField("theme", serializer=ThemeSerializer()),
        APIField("key_stages", serializer=KeyStageSerializer(many=True)),
        APIField("time_periods", serializer=TimePeriodSerializer(many=True)),
        APIField("themes", serializer=ThemeSerializer(many=True)),
    ]

    edit_handler = TabbedInterface(
        [
            ObjectList(content_panels, heading="Content"),
            ObjectList(key_details_panels, heading="Key details"),
            ObjectList(promote_panels, heading="Promote"),
            ObjectList(BasePageWithRequiredIntro.settings_panels, heading="Settings"),
        ]
    )
