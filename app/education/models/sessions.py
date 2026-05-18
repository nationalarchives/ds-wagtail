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

from ..blocks import SessionDescriptionBlock, VenueDetailsBlock
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

    session_duration = models.CharField(
        verbose_name=_("session duration"),
        help_text=_(
            "A clear description of the session duration, e.g. 1 hour, 1 to 2 hours."
        ),
        blank=True,
        max_length=160,
    )

    venue_details = StreamField(
        [("venue_details", VenueDetailsBlock())],
        blank=True,
        max_num=1,
        use_json_field=True,
        verbose_name=_("venue details"),
    )

    panels = [
        FieldPanel("location_type"),
        FieldPanel("session_duration"),
        FieldPanel("venue_details"),
    ]

    class Meta:
        verbose_name = _("session location")
        verbose_name_plural = _("session locations")
        ordering = ["sort_order"]

    def clean(self):
        super().clean()

        venue_data = {}
        if self.venue_details:
            venue_data = self.venue_details[0].value

        venue_name = (venue_data.get("venue_name") or "").strip()
        address_line_1 = (venue_data.get("address_line_1") or "").strip()
        address_line_2 = (venue_data.get("address_line_2") or "").strip()
        postcode = (venue_data.get("postcode") or "").strip()
        session_regions = venue_data.get("session_regions")

        has_venue_details = any([venue_name, address_line_1, address_line_2, postcode])

        if self.location_type == self.LocationType.CUSTOM and not venue_name:
            raise ValidationError(
                {"venue_details": _("Venue name is required for custom venue.")}
            )

        if self.location_type == self.LocationType.CUSTOM and not session_regions:
            raise ValidationError(
                {"venue_details": _("Region is required for custom venue.")}
            )

        if self.location_type != self.LocationType.CUSTOM and has_venue_details:
            raise ValidationError(
                {
                    "venue_details": _(
                        "Leave venue details empty unless location type is Custom venue."
                    )
                }
            )

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
        null=True, blank=True, verbose_name=_("session price")
    )

    price_detail = models.CharField(
        verbose_name=_("session price detail"),
        help_text=_(
            "An explanation of the price. Required if session price is filled in."
        ),
        blank=True,
        max_length=160,
    )

    booking_link = models.URLField(
        null=True,
        blank=True,
        help_text="Link to booking page",
        verbose_name="Booking link",
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
