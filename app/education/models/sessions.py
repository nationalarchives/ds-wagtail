from django.conf import settings
from django.core.exceptions import ValidationError
from django.db import models
from django.utils.functional import cached_property
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
from app.core.serializers import RichTextSerializer

from ..blocks import SessionDescriptionBlock
from ..serializers import (
    KeyStageSerializer,
    LinkedPageSerializer,
    SessionLocationSerializer,
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
        ONLINE = "online", "Online"
        NATIONAL_ARCHIVES = "national_archives", "At The National Archives"
        YOUR_SCHOOL = "your_school", "At your school"
        CUSTOM = "custom", "Custom venue"

    class Regions(models.TextChoices):
        SOUTH_EAST = "south_east", "South East and London"
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
        verbose_name="location type",
        help_text="Choose a standard location or Custom venue.",
        null=True,
    )

    duration = models.CharField(
        verbose_name="duration",
        help_text="A clear description of the session duration for this location, e.g. 1 hour, 1 to 2 hours.",
        blank=True,
        null=True,
        max_length=160,
    )

    region = models.CharField(
        max_length=32,
        choices=Regions.choices,
        verbose_name="region",
        help_text="The region where the session is offered. Required for schools and custom venues.",
        null=True,
        blank=True,
    )

    venue_name = models.CharField(
        blank=True,
        null=True,
        max_length=255,
        verbose_name="Venue name",
        help_text="Required only when location type is Custom venue.",
    )

    address_line_1 = models.CharField(
        blank=True,
        null=True,
        max_length=255,
        verbose_name="Address line 1",
        help_text="Required only when location type is Custom venue.",
    )

    address_line_2 = models.CharField(
        blank=True,
        null=True,
        max_length=255,
        verbose_name="Address line 2",
    )

    postcode = models.CharField(
        blank=True,
        null=True,
        max_length=20,
        verbose_name="Postcode",
        help_text="Required only when location type is Custom venue.",
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
            heading="Custom venue address details",
        ),
    ]

    class Meta:
        verbose_name = "session location"
        verbose_name_plural = "session locations"
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
                errors["venue_name"] = "Venue name is required for custom venue."
            if not address_line_1:
                errors["address_line_1"] = (
                    "Address line 1 is required for custom venue."
                )
            if not postcode:
                errors["postcode"] = "Postcode is required for custom venue."
        elif has_venue_details:
            errors["venue_name"] = (
                "Venue details should only be provided for custom venue location type."
            )

        if location_requires_region and not region:
            errors["region"] = (
                "Region is required for school or custom venue location types."
            )
        elif region and not location_requires_region:
            errors["region"] = (
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
        verbose_name="selected page",
    )

    class Meta:
        verbose_name = "related education session"
        ordering = ["sort_order"]


class EducationSessionPage(
    EducationTaxonomyMixin,
    PublishedDateMixin,
    RequiredHeroImageMixin,
    BasePageWithRequiredIntro,
):
    """A page to display an education session"""

    @cached_property
    def type_label(self) -> str:
        return "Education session"

    parent_page_types = [
        "education.EducationSessionsListingPage",
    ]

    start_date = models.DateField(
        verbose_name="start date",
        null=True,
        blank=True,
        help_text="If neither start nor end date is added this will default to 'All Year'",
    )

    end_date = models.DateField(
        verbose_name="end date",
        null=True,
        blank=True,
        help_text="If neither start nor end date is added this will default to 'All Year'",
    )

    price = models.FloatField(null=True, blank=True, verbose_name="price")

    price_detail = models.CharField(
        verbose_name="price detail",
        help_text="An explanation of the price. Required if price is filled in.",
        blank=True,
        null=True,
        max_length=160,
    )

    booking_link = models.URLField(
        null=True,
        blank=True,
        help_text="Link to booking page",
        verbose_name="Booking link",
    )

    description = StreamField(
        [("content_section", SessionDescriptionBlock())],
        verbose_name="description",
        blank=True,
        null=True,
        min_num=1,
    )

    curriculum_connection_description = RichTextField(
        features=settings.EXPANDED_RICH_TEXT_FEATURES,
        verbose_name="curriculum connection description",
        help_text="A description of how the session connects to the curriculum. This is optional but can help teachers understand the relevance of the session to their teaching.",
        null=True,
        blank=True,
    )

    highlights = StreamField(
        [("image_gallery", ImageGalleryBlock())],
        blank=True,
        help_text="Optional image gallery to show what to expect from the session.",
        max_num=1,
    )

    def clean(self):
        super().clean()

        if self.price and not self.price_detail:
            raise ValidationError(
                {
                    "price_detail": "Price detail is required when a session price is specified."
                }
            )
        if self.price is None and self.price_detail:
            raise ValidationError(
                {"price": "Price is required when price detail is specified."}
            )
        if (
            self.start_date is not None
            and self.end_date is not None
            and self.start_date > self.end_date
        ):
            raise ValidationError(
                {"end_date": "End date must not be before start date."}
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
                heading="More education sessions",
                help_text="Education sessions that are selected to be shown in the related education sessions section",
            ),
        ]
    )

    key_details_panels = [
        MultiFieldPanel(
            [
                FieldPanel("start_date"),
                FieldPanel("end_date"),
                MultiFieldPanel(
                    [
                        FieldPanel("price"),
                        FieldPanel("price_detail"),
                    ],
                    heading="Session price",
                ),
                InlinePanel(
                    "session_locations",
                    label="Location",
                    heading="Session locations",
                    min_num=1,
                ),
                FieldPanel("booking_link"),
            ],
        ),
    ]

    promote_panels = (
        PublishedDateMixin.promote_panels
        + BasePageWithRequiredIntro.promote_panels
        + EducationTaxonomyMixin.taxonomy_promote_panels()
    )

    default_api_fields = BasePageWithRequiredIntro.default_api_fields + [
        APIField("key_stages", serializer=KeyStageSerializer(many=True)),
        APIField("time_periods", serializer=TimePeriodSerializer(many=True)),
        APIField("themes", serializer=ThemeSerializer(many=True)),
    ]

    api_fields = (
        BasePageWithRequiredIntro.api_fields
        + RequiredHeroImageMixin.api_fields
        + [
            PublishedDateMixin.get_published_date_apifield(),
            PublishedDateMixin.get_is_newly_published_apifield(),
        ]
        + [
            APIField("description"),
            APIField(
                "curriculum_connection_description", serializer=RichTextSerializer()
            ),
            APIField("highlights"),
            APIField(
                "related_education_sessions", serializer=LinkedPageSerializer(many=True)
            ),
            APIField("start_date"),
            APIField("end_date"),
            APIField("price"),
            APIField("price_detail"),
            APIField(
                "session_locations",
                serializer=SessionLocationSerializer(many=True),
            ),
            APIField("booking_link"),
            # TODO: primary tags?
            # APIField("key_stage", serializer=KeyStageSerializer()),
            # APIField("time_period", serializer=TimePeriodSerializer()),
            # APIField("theme", serializer=ThemeSerializer()),
            APIField("key_stages", serializer=KeyStageSerializer(many=True)),
            APIField("time_periods", serializer=TimePeriodSerializer(many=True)),
            APIField("themes", serializer=ThemeSerializer(many=True)),
        ]
    )

    edit_handler = TabbedInterface(
        [
            ObjectList(content_panels, heading="Content"),
            ObjectList(key_details_panels, heading="Key details"),
            ObjectList(promote_panels, heading="Promote"),
            ObjectList(BasePageWithRequiredIntro.settings_panels, heading="Settings"),
        ]
    )
