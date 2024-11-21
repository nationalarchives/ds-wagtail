from django.conf import settings
from django.core.exceptions import ValidationError
from django.db import models
from django.utils import timezone
from django.utils.functional import cached_property
from django.utils.translation import gettext_lazy as _

from modelcluster.fields import ParentalKey
from wagtail.admin.panels import (
    FieldPanel,
    FieldRowPanel,
    InlinePanel,
    MultiFieldPanel,
    ObjectList,
    TabbedInterface,
)
from wagtail.api import APIField
from wagtail.fields import RichTextField, StreamField
from wagtail.images import get_image_model_string
from wagtail.models import Orderable
from wagtail.search import index
from wagtail.snippets.models import register_snippet

from etna.articles.models import ArticleTagMixin
from etna.collections.models import TopicalPageMixin
from etna.core.blocks import ImageGalleryBlock, LargeCardLinksBlock, ReviewBlock
from etna.core.models import (
    AccentColourMixin,
    BasePageWithRequiredIntro,
    HeroImageMixin,
)
from etna.core.serializers import DefaultPageSerializer, RichTextSerializer

from .blocks import WhatsOnPromotedLinksBlock
from .forms import EventPageForm


class VenueType(models.TextChoices):
    """
    This model is used to add venue types to event pages.
    """

    ONLINE = "online", _("Online")
    IN_PERSON = "in_person", _("In person")
    HYBRID = "hybrid", _("In person and online")


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
    )

    slug = models.SlugField(
        max_length=255,
        verbose_name=_("slug"),
        unique=True,
    )

    class Meta:
        verbose_name = _("event type")
        verbose_name_plural = _("event types")
        verbose_name_public = _("event")

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
    )

    slug = models.SlugField(
        max_length=255,
        verbose_name=_("slug"),
        unique=True,
    )

    class Meta:
        verbose_name = _("Audience type")
        verbose_name_plural = _("Audience types")

    def __str__(self):
        return self.name


class EventAudienceType(Orderable):
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
        related_name="event_audience_types",
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
    )

    slug = models.SlugField(
        max_length=255,
        verbose_name=_("slug"),
        unique=True,
    )

    class Meta:
        verbose_name = _("Access type")
        verbose_name_plural = _("Access types")

    def __str__(self):
        return self.name


class EventAccessType(Orderable):
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
        related_name="event_access_types",
    )


class EventHost(Orderable):
    """
    This model is used to add host information to event pages.
    """

    page = ParentalKey(
        "wagtailcore.Page",
        on_delete=models.CASCADE,
        related_name="hosts",
    )

    name = models.CharField(
        max_length=100,
        verbose_name=_("name"),
    )

    description = models.CharField(
        max_length=200,
        verbose_name=_("description"),
        blank=True,
    )

    image = models.ForeignKey(
        get_image_model_string(),
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="+",
    )

    panels = [
        FieldPanel("name"),
        FieldPanel("description"),
        FieldPanel("image"),
    ]


class EventSpeaker(Orderable):
    """
    This model is used to add speaker information to event pages.
    """

    page = ParentalKey(
        "wagtailcore.Page",
        on_delete=models.CASCADE,
        related_name="speakers",
    )

    name = models.CharField(
        max_length=100,
        verbose_name=_("name"),
    )

    description = models.CharField(
        max_length=200,
        verbose_name=_("description"),
        blank=True,
    )

    image = models.ForeignKey(
        get_image_model_string(),
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="+",
    )

    panels = [
        FieldPanel("name"),
        FieldPanel("description"),
        FieldPanel("image"),
    ]


class EventSession(models.Model):
    """
    This model is used to add sessions to an event
    e.g. 28th September @ 9:00, 29th September @ 10:30, 30th September @ 12:00.
    These will link to the Eventbrite page.
    """

    page = ParentalKey(
        "wagtailcore.Page",
        on_delete=models.CASCADE,
        related_name="sessions",
    )

    """
    Session ID will be used to hold the Eventbrite "event ID"
    in Event Series pages, for each occurrence of the event.
    For single events, it will be blank. We will also leave
    it blank for editor created events, as we won't have an
    Eventbrite event ID for these.
    """
    session_id = models.CharField(
        verbose_name=_("session ID"),
        null=True,
        blank=True,
        editable=False,
        max_length=35,
    )

    start = models.DateTimeField(
        verbose_name=_("starts at"),
    )

    end = models.DateTimeField(
        verbose_name=_("ends at"),
    )

    panels = [
        FieldPanel("start"),
        FieldPanel("end"),
    ]

    class Meta:
        verbose_name = _("session")
        verbose_name_plural = _("sessions")
        ordering = ["start"]


class WhatsOnPage(BasePageWithRequiredIntro):
    """WhatsOnPage

    A page for listing events.
    """

    featured_event = models.ForeignKey(
        "whatson.EventPage",
        null=True,
        blank=True,
        verbose_name=_("featured event"),
        on_delete=models.SET_NULL,
        related_name="+",
    )
    promoted_links = StreamField(
        [("promoted_links", WhatsOnPromotedLinksBlock())],
        blank=True,
        max_num=1,
    )
    large_card_links = StreamField(
        [("large_card_links", LargeCardLinksBlock())],
        blank=True,
        max_num=1,
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
        "whatson.ExhibitionPage",
    ]

    max_count = 1

    content_panels = BasePageWithRequiredIntro.content_panels + [
        FieldPanel("featured_event"),
        FieldPanel("promoted_links"),
        FieldPanel("large_card_links"),
    ]


class EventPage(ArticleTagMixin, TopicalPageMixin, BasePageWithRequiredIntro):
    """EventPage

    A page for an event.
    """

    # Content
    lead_image = models.ForeignKey(
        get_image_model_string(),
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="+",
    )

    # Event information
    event_type = models.ForeignKey(
        EventType,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="+",
    )

    start_date = models.DateTimeField(
        verbose_name=_("start date"),
        null=True,
        editable=False,
    )

    end_date = models.DateTimeField(
        verbose_name=_("end date"),
        null=True,
        editable=False,
    )

    description = RichTextField(
        verbose_name=_("description"),
        blank=True,
        help_text=_("A description of the event."),
    )

    useful_info = RichTextField(
        verbose_name=_("need to know"),
        blank=True,
        help_text=_("Useful information about the event."),
    )

    # Text for need to know button
    need_to_know_button_text = models.CharField(
        verbose_name=_("need to know button text"),
        max_length=30,
        blank=True,
        help_text=_("The text of the need to know button."),
    )

    need_to_know_button_link = models.URLField(
        max_length=255,
        verbose_name=_("need to know link"),
        blank=True,
        help_text=_("The website for need to know info."),
    )

    target_audience = RichTextField(
        verbose_name=_("who it's for"),
        blank=True,
        help_text=_("Info about the target audience for the event."),
    )

    # Venue information
    venue_type = models.CharField(
        verbose_name=_("venue type"),
        choices=VenueType.choices,
        default=VenueType.IN_PERSON,
        blank=True,
        max_length=30,
    )

    venue_website = models.URLField(
        max_length=255,
        verbose_name=_("venue website"),
        blank=True,
        help_text=_("The website for the venue."),
    )

    venue_address = RichTextField(
        verbose_name=_("venue address"),
        blank=True,
        help_text=_("The address of the venue."),
    )

    venue_space_name = models.CharField(
        max_length=255,
        verbose_name=_("venue space name"),
        blank=True,
        help_text=_("The name of the venue space."),
    )

    venue_directions = models.URLField(
        max_length=255,
        verbose_name=_("venue directions"),
        null=True,
        blank=True,
        help_text=_("A link to the venue's 'How to find us' page."),
    )

    video_conference_info = RichTextField(
        verbose_name=_("video conference info"),
        blank=True,
        help_text=_("Useful information about the video conference."),
    )

    # Booking information
    registration_url = models.URLField(
        max_length=255,
        verbose_name=_("registration url"),
        editable=False,
    )

    min_price = models.IntegerField(
        verbose_name=_("minimum price"),
        default=0,
        editable=False,
    )

    max_price = models.IntegerField(
        verbose_name=_("maximum price"),
        default=0,
        editable=False,
    )

    """
    We will use this field to hold the event ID from Eventbrite,
    or if it is the parent page of an Event Series, it will hold
    the "series_id" from Eventbrite. For editor created events,
    it will be blank.
    """
    eventbrite_id = models.CharField(
        max_length=255,
        verbose_name=_("eventbrite ID"),
        null=True,
        editable=False,
    )
    # The booking info fields above will be brought in from the API when we have it.

    registration_info = RichTextField(
        verbose_name=_("registration info"),
        blank=True,
        help_text=_("Additional information about how to register for the event."),
        features=settings.RESTRICTED_RICH_TEXT_FEATURES,
    )

    contact_info = RichTextField(
        verbose_name=_("contact info"),
        blank=True,
        help_text=_("Information about who to contact regarding the event."),
        features=settings.RESTRICTED_RICH_TEXT_FEATURES,
    )

    # Promote tab
    short_title = models.CharField(
        max_length=50,
        verbose_name=_("short title"),
        blank=True,
        help_text=_(
            "A short title for the event. This will be used in the event listings."
        ),
    )

    # DataLayerMixin overrides
    gtm_content_group = "What's On"

    class Meta:
        verbose_name = _("event page")

    content_panels = BasePageWithRequiredIntro.content_panels + [
        FieldPanel("lead_image"),
        MultiFieldPanel(
            [
                FieldPanel("event_type"),
                FieldPanel("start_date", read_only=True),
                FieldPanel("end_date", read_only=True),
                InlinePanel(
                    "sessions",
                    heading=_("Sessions"),
                    min_num=1,
                ),
                FieldPanel("description"),
                FieldPanel("useful_info"),
                FieldPanel("need_to_know_button_text"),
                FieldPanel("need_to_know_button_link"),
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
                    "hosts",
                    heading=_("Host information"),
                    help_text=_(
                        "If the event has more than one host, please add these in order of relevance from most to least."
                    ),
                ),
                InlinePanel(
                    "speakers",
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
                FieldPanel("venue_directions"),
                FieldPanel("video_conference_info"),
            ],
            heading=_("Venue information"),
        ),
        MultiFieldPanel(
            [
                FieldPanel("registration_url", read_only=True),
                FieldPanel("min_price", read_only=True),
                FieldPanel("max_price", read_only=True),
                FieldPanel("registration_info"),
                FieldPanel("contact_info"),
            ],
            heading=_("Booking information"),
        ),
    ]

    @cached_property
    def price_range(self):
        """
        Returns the price range for the event.
        """
        if self.max_price == 0:
            return "Free"
        elif self.min_price == self.max_price:
            return f"{self.min_price}"
        else:
            if self.min_price == 0:
                return f"Free - {self.max_price}"
            return f"{self.min_price} - {self.max_price}"

    @property
    def event_status(self):
        """
        Returns the event status based on different conditions.
        """
        if self.start_date.date() <= (
            timezone.now().date() + timezone.timedelta(days=5)
        ):
            return "Last chance"

    @cached_property
    def primary_access_type(self):
        """
        Returns the primary access type for the event.
        """
        if primary_access := self.event_access_types.first():
            return primary_access.access_type

    @cached_property
    def date_time_range(self):
        format_day_date_and_time = "%A %-d %B %Y, %H:%M"
        format_date_only = "%-d %B %Y"
        format_time_only = "%H:%M"
        format_day_and_date = "%A %-d %B %Y"
        # One session on one date where start and end times are the same
        # return eg. Monday 1 January 2024, 19:00
        if (self.start_date == self.end_date) and (len(self.sessions.all()) == 1):
            return self.start_date.strftime(format_day_date_and_time)
        # One session on one date where there are values for both start time and end time
        # eg. Monday 1 January 2024, 19:00–20:00 (note this uses an en dash)
        dates_same = self.start_date.date() == self.end_date.date()
        if (
            dates_same
            and (self.start_date.time() != self.end_date.time())
            and (len(self.sessions.all()) == 1)
        ):
            return f"{self.start_date.strftime(format_day_date_and_time)}–{self.end_date.strftime(format_time_only)}"
        # Multiple sessions on one date
        # Eg. Monday 1 January 2024
        if dates_same and len(self.sessions.all()) > 1:
            return self.start_date.strftime(format_day_and_date)
        # Event has multiple dates
        # Eg. 1 January 2024 to 5 January 2024
        if not dates_same:
            return f"{self.start_date.strftime(format_date_only)} to {self.end_date.strftime(format_date_only)}"

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

    def serializable_data(self):
        # Keep aggregated field values out of revision content

        data = super().serializable_data()

        for field_name in ("start_date", "end_date"):
            data.pop(field_name, None)

        return data

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
        min_start = None
        max_end = None
        for session in self.sessions.all():
            if min_start is None or session.start < min_start:
                min_start = session.start
            if max_end is None or session.end > max_end:
                max_end = session.end

        self.start_date = min_start
        self.end_date = max_end

        super().save(*args, **kwargs)

    promote_panels = (
        BasePageWithRequiredIntro.promote_panels
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
        BasePageWithRequiredIntro.search_fields
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

    base_form_class = EventPageForm


class ExhibitionPage(
    ArticleTagMixin,
    AccentColourMixin,
    HeroImageMixin,
    TopicalPageMixin,
    BasePageWithRequiredIntro,
):
    """ExhibitionPage

    An event where editors can create exhibitions. Exhibitions do not come
    from Eventbrite - they are internal TNA exhibitions.
    """

    # Hero section
    subtitle = models.CharField(
        max_length=255,
        verbose_name=_("subtitle"),
        blank=True,
        help_text=_("A subtitle for the event."),
    )

    # Key details section
    start_date = models.DateTimeField(
        verbose_name=_("start date"),
        null=True,
    )

    end_date = models.DateTimeField(
        verbose_name=_("end date"),
        null=True,
    )

    price = models.IntegerField(
        verbose_name=_("price"),
        default=0,
    )

    booking_details = RichTextField(
        max_length=40,
        verbose_name=_("booking details"),
        blank=True,
        help_text=_("Information about how to book tickets for the exhibition."),
    )

    audience_heading = models.CharField(
        max_length=40,
        verbose_name=_("audience heading"),
        blank=True,
        help_text=_("The heading for the audience detail section."),
    )

    audience_detail = models.CharField(
        max_length=40,
        verbose_name=_("audience detail"),
        blank=True,
        help_text=_("The text for the audience detail section."),
    )

    # Body section
    description = RichTextField(
        verbose_name=_("description"),
        help_text=_("A description of the exhibition."),
        features=settings.EXPANDED_RICH_TEXT_FEATURES,
    )

    # email_signup = ...

    exhibition_highlights = StreamField(
        [("exhibition_highlights", ImageGalleryBlock())],
        blank=True,
        max_num=1,
    )

    review = StreamField(
        [("review", ReviewBlock())],
        blank=True,
        max_num=1,
    )

    # video = ...

    # Related content section
    related_pages_title = models.CharField(
        max_length=255,
        blank=True,
        help_text=_("The title to display for the related content section."),
    )

    featured_page = models.ForeignKey(
        "wagtailcore.Page",
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="+",
    )

    # related_pages = StreamField(RelatedContentBlock(), blank=True, null=True)

    # shop = ...

    # Plan your visit section

    # DataLayerMixin overrides
    gtm_content_group = "What's On"

    class Meta:
        verbose_name = _("exhibition page")

    content_panels = BasePageWithRequiredIntro.content_panels + [
        MultiFieldPanel(
            [
                FieldPanel("hero_image"),
                FieldPanel("hero_image_caption"),
                FieldPanel("subtitle"),
                FieldPanel("accent_colour"),
            ],
            heading=_("Hero section"),
        ),
        MultiFieldPanel(
            [
                FieldPanel("description"),
                # FieldPanel("email_signup"),
                FieldPanel("review"),
                FieldPanel("exhibition_highlights"),
                # FieldPanel("video"),
            ],
            heading=_("Content"),
        ),
        MultiFieldPanel(
            [
                FieldPanel("related_pages_title"),
                FieldPanel("featured_page"),
                # FieldPanel("related_pages"),
                # FieldPanel("shop"),
            ],
            heading=_("Related content"),
        ),
    ]

    key_details_panels = [
        FieldRowPanel(
            [
                FieldPanel("start_date"),
                FieldPanel("end_date"),
            ],
            heading=_("Dates"),
        ),
        MultiFieldPanel(
            [
                FieldPanel("price"),
                FieldPanel("booking_details"),
            ],
            heading=_("Price details"),
        ),
        MultiFieldPanel(
            [
                FieldPanel("audience_heading"),
                FieldPanel("audience_detail"),
            ],
            heading=_("Audience details"),
        ),
    ]

    promote_panels = (
        BasePageWithRequiredIntro.promote_panels
        + ArticleTagMixin.promote_panels
        + [
            TopicalPageMixin.get_topics_inlinepanel(),
            TopicalPageMixin.get_time_periods_inlinepanel(),
        ]
    )

    api_fields = (
        BasePageWithRequiredIntro.api_fields
        + HeroImageMixin.api_fields
        + AccentColourMixin.api_fields
        + [
            APIField("subtitle"),
            APIField("start_date"),
            APIField("end_date"),
            APIField("price"),
            APIField("price_label"),
            APIField("booking_details", serializer=RichTextSerializer()),
            APIField("audience_heading"),
            APIField("audience_detail"),
            APIField("description", serializer=RichTextSerializer()),
            # APIField("email_signup"),
            APIField("exhibition_highlights"),
            APIField("review"),
            # APIField("video"),
            APIField("related_pages_title"),
            APIField("featured_page", serializer=DefaultPageSerializer()),
            # APIField("related_pages"),
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

    search_fields = (
        BasePageWithRequiredIntro.search_fields
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

    @cached_property
    def price_label(self):
        """
        Returns a human readable price for the event.
        """
        if self.price == 0:
            return "Free"
        return f"From {self.price}"

    def clean(self):
        """
        Check that the venue address and video conference information are
        provided for the correct venue type.
        """

        if self.start_date and self.end_date:
            if self.start_date > self.end_date:
                raise ValidationError(
                    {
                        "start_date": _("The start date must be before the end date."),
                        "end_date": _("The end date must be after the start date."),
                    }
                )
        return super().clean()
