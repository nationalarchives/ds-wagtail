from django.core.exceptions import ValidationError
from django.db import models
from django.utils.functional import cached_property
from django.utils.translation import gettext_lazy as _

from modelcluster.fields import ParentalKey
from wagtail.admin.panels import FieldPanel, InlinePanel, MultiFieldPanel
from wagtail.fields import RichTextField
from wagtail.images import get_image_model_string
from wagtail.models import Orderable
from wagtail.search import index
from wagtail.snippets.models import register_snippet

from etna.articles.models import ArticleTagMixin
from etna.collections.models import TopicalPageMixin
from etna.core.models import BasePageWithIntro


class VenueType(models.TextChoices):
    """
    This model is used to add venue types to event pages.
    """

    ONLINE = "online", _("Online")
    IN_PERSON = "in_person", _("In person")
    HYBRID = "hybrid", _("Hybrid")


@register_snippet
class EventType(models.Model):
    """
    This snippet model is used so that editors can add event types,
    which we use via the event_type ForeignKey to add event types
    to event pages.
    """

    name = models.CharField(
        max_length=255,
        verbose_name=_("name"),
        help_text=_("The name of the event type."),
    )

    class Meta:
        verbose_name = _("Event type")
        verbose_name_plural = _("Event types")

    def __str__(self):
        return self.name


@register_snippet
class AudienceType(models.Model):
    """
    This snippet model is used so that editors can add audience types,
    which we use via the audience_type ForeignKey to add audience types
    to event pages.
    """

    name = models.CharField(
        max_length=255,
        verbose_name=_("name"),
        help_text=_("The name of the audience type."),
    )

    class Meta:
        verbose_name = _("Audience type")
        verbose_name_plural = _("Audience types")

    def __str__(self):
        return self.name


class AudienceTypeOrderable(Orderable):
    """
    This model is used to add multiple audience types to event pages.
    """

    page = ParentalKey(
        "wagtailcore.Page",
        on_delete=models.CASCADE,
        related_name="event_audience_types",
    )

    audience_type = models.ForeignKey(
        "whatson.AudienceType",
        on_delete=models.CASCADE,
        related_name="audience_types",
    )


@register_snippet
class AccessType(models.Model):
    """
    This snippet model is used so that editors can add access types,
    which we use via the AccessTypeOrderable to add multiple access
    types to event pages.
    """

    name = models.CharField(
        max_length=255,
        verbose_name=_("name"),
        help_text=_("The type of access descriptor"),
    )

    class Meta:
        verbose_name = _("Access type")
        verbose_name_plural = _("Access types")

    panels = [
        FieldPanel("name"),
    ]

    def __str__(self):
        return self.name


class AccessTypeOrderable(Orderable):
    """
    This model is used to add multiple access types to event pages.
    """

    page = ParentalKey(
        "wagtailcore.Page",
        on_delete=models.CASCADE,
        related_name="event_access_types",
    )

    access_type = models.ForeignKey(
        "whatson.AccessType",
        on_delete=models.CASCADE,
        related_name="access_types",
    )


class Host(Orderable):
    """
    This model is used to add host information to event pages.
    """

    page = ParentalKey(
        "wagtailcore.Page",
        on_delete=models.CASCADE,
        related_name="host_information",
    )

    # When we have an author page, we will add a ForeignKey to that here.
    # The below fields will remain when we have an author page, but will be
    # optional, if there is no page for the host/author.

    host_name = models.CharField(
        max_length=100,
        verbose_name=_("host name"),
        help_text=_("The name of the host."),
        blank=True,
        null=True,
    )

    host_description = models.CharField(
        max_length=200,
        verbose_name=_("host description"),
        help_text=_("The description of the host."),
        blank=True,
        null=True,
    )

    host_image = models.ForeignKey(
        get_image_model_string(),
        null=True,
        blank=False,
        on_delete=models.SET_NULL,
        related_name="+",
    )

    panels = [
        FieldPanel("host_name"),
        FieldPanel("host_description"),
        FieldPanel("host_image"),
    ]


class Speaker(Orderable):
    """
    This model is used to add speaker information to event pages.
    """

    page = ParentalKey(
        "wagtailcore.Page",
        on_delete=models.CASCADE,
        related_name="speaker_information",
    )

    # When we have an author page, we will add a ForeignKey to that here.
    # The below fields will remain when we have an author page, but will be
    # optional, if there is no page for the speaker/author.

    speaker_name = models.CharField(
        max_length=100,
        verbose_name=_("speaker name"),
        help_text=_("The name of the speaker."),
        blank=True,
        null=True,
    )

    speaker_description = models.CharField(
        max_length=200,
        verbose_name=_("speaker description"),
        help_text=_("The description of the speaker."),
        blank=True,
        null=True,
    )

    speaker_image = models.ForeignKey(
        get_image_model_string(),
        null=True,
        blank=False,
        on_delete=models.SET_NULL,
        related_name="+",
    )

    panels = [
        FieldPanel("speaker_name"),
        FieldPanel("speaker_description"),
        FieldPanel("speaker_image"),
    ]


class EventSession(Orderable):
    """
    This model is used to add sessions to an event
    e.g. 28th September @ 9:00, 29th September @ 10:30, 30th September @ 12:00.
    These will link to the Eventbrite page.
    """

    page = ParentalKey(
        "wagtailcore.Page",
        on_delete=models.CASCADE,
        related_name="event_sessions",
    )

    session_start_date = models.DateTimeField(
        verbose_name=_("session start date"),
        null=True,
        blank=False,
        help_text=_("The date and time the session starts."),
    )

    session_end_date = models.DateTimeField(
        verbose_name=_("session end date"),
        null=True,
        blank=False,
        help_text=_("The date and time the session ends."),
    )

    panels = [
        FieldPanel("session_start_date"),
        FieldPanel("session_end_date"),
    ]


class WhatsOnPage(BasePageWithIntro):
    """WhatsOnPage

    A page for listing events.
    """

    @cached_property
    def events(self):
        """
        Returns a queryset of events that are children of this page.
        """
        return (
            self.get_children()
            .type(EventPage)
            .specific()
            .live()
            .public()
            .order_by("eventpage__start_date")
        )

    # DataLayerMixin overrides
    gtm_content_group = "What's On"

    class Meta:
        verbose_name = _("What's On page")

    parent_page_types = [
        "home.HomePage",
    ]
    subpage_types = [
        "whatson.EventPage",
    ]

    content_panels = BasePageWithIntro.content_panels


class EventPage(ArticleTagMixin, TopicalPageMixin, BasePageWithIntro):
    """EventPage

    A page for an event.
    """

    # Content
    lead_image = models.ForeignKey(
        get_image_model_string(),
        null=True,
        blank=False,
        on_delete=models.SET_NULL,
        related_name="+",
    )

    # Event information
    event_type = models.ForeignKey(
        EventType,
        null=True,
        blank=False,
        on_delete=models.SET_NULL,
        related_name="+",
    )

    # Start and end date will be brought in from the API when we have it.
    start_date = models.DateTimeField(
        verbose_name=_("start date"),
        null=True,
        blank=True,
        help_text=_("The date and time the event starts."),
    )

    end_date = models.DateTimeField(
        verbose_name=_("end date"),
        null=True,
        blank=True,
        help_text=_("The date and time the event ends."),
    )

    description = RichTextField(
        verbose_name=_("description"),
        null=True,
        blank=True,
        help_text=_("A description of the event."),
    )

    useful_info = RichTextField(
        verbose_name=_("need to know"),
        null=True,
        blank=True,
        help_text=_("Useful information about the event."),
    )

    target_audience = RichTextField(
        verbose_name=_("who it's for"),
        null=True,
        blank=True,
        help_text=_("Info about the target audience for the event."),
    )

    # Venue information
    venue_type = models.CharField(
        max_length=15,
        verbose_name=_("venue type"),
        null=False,
        blank=False,
        choices=VenueType.choices,
        default=VenueType.IN_PERSON,
        help_text=_("The type of venue for the event."),
    )

    venue_website = models.URLField(
        max_length=255,
        verbose_name=_("venue website"),
        null=True,
        blank=True,
        help_text=_("The website for the venue."),
    )

    venue_address = RichTextField(
        verbose_name=_("venue address"),
        null=True,
        blank=True,
        help_text=_("The address of the venue."),
    )

    venue_space_name = models.CharField(
        max_length=255,
        verbose_name=_("venue space name"),
        null=True,
        blank=True,
        help_text=_("The name of the venue space."),
    )

    video_conference_info = RichTextField(
        verbose_name=_("video conference info"),
        null=True,
        blank=True,
        help_text=_("Information about the video conference."),
    )

    # Booking information
    booking_type = models.CharField(
        max_length=20,
        verbose_name=_("booking type"),
        null=False,
        blank=False,
        default="Drop in",
        help_text=_("The type of booking for the event."),
    )

    registration_url = models.URLField(
        max_length=255,
        verbose_name=_("registration url"),
        null=True,
        blank=True,
        help_text=_("The URL for the event registration."),
    )

    registration_cost = models.IntegerField(
        verbose_name=_("registration cost"),
        null=True,
        blank=True,
        help_text=_("The cost of registration for the event."),
    )
    # The three fields above will be brought in from the API when we have it.

    registration_info = RichTextField(
        verbose_name=_("registration info"),
        null=True,
        blank=True,
        help_text=_("Information about how to register for the event."),
    )

    contact_info = RichTextField(
        verbose_name=_("contact info"),
        null=True,
        blank=True,
        help_text=_("Information about who to contact for the event."),
    )

    # Promote tab
    short_title = models.CharField(
        max_length=50,
        verbose_name=_("short title"),
        help_text=_(
            "A short title for the event. This will be used in the event listings."
        ),
        blank=False,
        null=True,
    )

    # DataLayerMixin overrides
    gtm_content_group = "What's On"

    class Meta:
        verbose_name = _("Event page")

    content_panels = BasePageWithIntro.content_panels + [
        FieldPanel("lead_image"),
        MultiFieldPanel(
            [
                FieldPanel("event_type"),
                FieldPanel("start_date", read_only=True),
                FieldPanel("end_date", read_only=True),
                InlinePanel(
                    "event_sessions",
                    heading=_("Event sessions"),
                    help_text=_("List of event sessions, ordered from first to last."),
                ),
                FieldPanel("description"),
                FieldPanel("useful_info"),
                FieldPanel("target_audience"),
                InlinePanel(
                    "event_access_types",
                    heading=_("Access types"),
                    help_text=_(
                        "If the event has more than one access type, please add these in order of relevance from most to least."
                    ),
                ),
                InlinePanel(
                    "event_audience_types",
                    heading=_("Audience types"),
                    help_text=_(
                        "If the event has more than one audience type, please add these in order of relevance from most to least."
                    ),
                ),
                InlinePanel(
                    "host_information",
                    heading=_("Host information"),
                    help_text=_(
                        "If the event has more than one host, please add these in order of relevance from most to least."
                    ),
                ),
                InlinePanel(
                    "speaker_information",
                    heading=_("Speaker information"),
                    help_text=_(
                        "If the event has more than one speaker, please add these in order of relevance from most to least."
                    ),
                ),
            ],
            heading=_("Event information"),
        ),
        MultiFieldPanel(
            [
                FieldPanel("venue_type"),
                FieldPanel("venue_website"),
                FieldPanel("venue_address"),
                FieldPanel("venue_space_name"),
                FieldPanel("video_conference_info"),
            ],
            heading=_("Venue information"),
        ),
        MultiFieldPanel(
            [
                FieldPanel("booking_type", read_only=True),
                FieldPanel("registration_url", read_only=True),
                FieldPanel("registration_cost", read_only=True),
                FieldPanel("registration_info"),
                FieldPanel("contact_info"),
            ],
            heading=_("Booking information"),
        ),
    ]

    def clean(self):
        """
        Check that the venue address and video conference information are
        provided for the correct venue type.
        """

        if self.venue_type:
            if self.venue_type == VenueType.HYBRID and (
                not self.venue_address or not self.video_conference_info
            ):
                raise ValidationError(
                    {
                        "venue_address": _(
                            "The venue address is required for hybrid events."
                        ),
                        "venue_space_name": _(
                            "The venue space name is required for hybrid events."
                        ),
                        "video_conference_info": _(
                            "The video conference information is required for hybrid events."
                        ),
                    }
                )
            elif self.venue_type == VenueType.IN_PERSON and not self.venue_address:
                raise ValidationError(
                    {
                        "venue_address": _(
                            "The venue address is required for in person events."
                        ),
                        "venue_space_name": _(
                            "The venue space name is required for hybrid events."
                        ),
                    }
                )
            elif self.venue_type == VenueType.ONLINE and not self.video_conference_info:
                raise ValidationError(
                    {
                        "video_conference_info": _(
                            "The video conference information is required for online events."
                        ),
                    }
                )
        return super().clean()

    def with_content_json(self, content):
        """
        Overrides Page.with_content_json() to ensure page's `start_date` and `end_date`
        value is always preserved between revisions.
        """
        obj = super().with_content_json(content)
        obj.start_date = self.start_date
        obj.end_date = self.end_date
        return obj

    def save(self, *args, **kwargs):
        """
        Set the event start date to the earliest session start date.
        Set the event end date to the latest session end date.
        """
        if self.event_sessions.all():
            self.start_date = (
                self.event_sessions.all()
                .order_by("session_start_date")
                .first()
                .session_start_date
            )
            self.end_date = (
                self.event_sessions.all()
                .order_by("session_end_date")
                .last()
                .session_end_date
            )

        super().save(*args, **kwargs)

        if self.latest_revision and (
            self.latest_revision.content["start_date"] != self.start_date
            or self.latest_revision.content["end_date"] != self.end_date
        ):
            # If `start_date` and `end_date` are unchanged in the latest revision,
            # the fields will remain blank when the page is next edited in Wagtail.
            # This allows us to update the values in the latest revision conetnt
            # to avoid unexpected resetting.
            self.latest_revision.content["start_date"] = self.start_date
            self.latest_revision.content["end_date"] = self.end_date
            self.latest_revision.save()

    promote_panels = (
        BasePageWithIntro.promote_panels
        + [
            FieldPanel("short_title"),
        ]
        + ArticleTagMixin.promote_panels
        + [
            TopicalPageMixin.get_topics_inlinepanel(),
            TopicalPageMixin.get_time_periods_inlinepanel(),
        ]
    )

    search_fields = (
        BasePageWithIntro.search_fields
        + ArticleTagMixin.search_fields
        + [
            index.SearchField("topic_names", boost=1),
            index.SearchField("time_period_names", boost=1),
        ]
    )

    parent_page_types = [
        "whatson.WhatsOnPage",
    ]
    subpage_types = []
