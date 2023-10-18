from django import forms
from django.core.exceptions import ValidationError
from django.db import models
from django.utils import timezone
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
    )

    slug = models.SlugField(
        max_length=255,
        verbose_name=_("slug"),
        unique=True,
    )

    class Meta:
        verbose_name = _("event type")
        verbose_name_plural = _("event types")

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


class WhatsOnPage(BasePageWithIntro):
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

    @cached_property
    def events(self):
        """
        Returns a queryset of events that are children of this page.
        """
        return EventPage.objects.child_of(self).live().public().order_by("start_date")

    def get_context(self, request, *args, **kwargs):
        context = super().get_context(request, *args, **kwargs)

        filter_form = EventFilterForm(request.GET)

        events = self.events

        if filter_form.is_valid():
            if filter_form.cleaned_data["date"]:
                events = events.filter(start_date__date=filter_form.cleaned_data["date"])
            if filter_form.cleaned_data["category"]:
                events = events.filter(event_type=filter_form.cleaned_data["category"])
            if filter_form.cleaned_data["online"]:
                events = events.filter(venue_type=VenueType.ONLINE)
            if filter_form.cleaned_data["family_friendly"]:
                events = events.filter(event_audience_types__audience_type__slug="families")
            self.events = events

        if events is None:
            context["no_events"] = True

        context["filter_form"] = filter_form

        return context

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

    max_count = 1

    content_panels = BasePageWithIntro.content_panels + [
        FieldPanel("featured_event"),
    ]


class EventPage(ArticleTagMixin, TopicalPageMixin, BasePageWithIntro):
    """EventPage

    A page for an event.
    """

    # Content
    lead_image = models.ForeignKey(
        get_image_model_string(),
        null=True,
        on_delete=models.SET_NULL,
        related_name="+",
    )

    # Event information
    event_type = models.ForeignKey(
        EventType,
        null=True,
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

    target_audience = RichTextField(
        verbose_name=_("who it's for"),
        blank=True,
        help_text=_("Info about the target audience for the event."),
    )

    # Venue information
    venue_type = models.CharField(
        max_length=15,
        verbose_name=_("venue type"),
        choices=VenueType.choices,
        default=VenueType.IN_PERSON,
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

    registration_cost = models.IntegerField(
        verbose_name=_("registration cost"),
        null=True,
        editable=False,
    )
    # The booking info fields above will be brought in from the API when we have it.

    registration_info = RichTextField(
        verbose_name=_("registration info"),
        blank=True,
        help_text=_("Additional information about how to register for the event."),
    )

    contact_info = RichTextField(
        verbose_name=_("contact info"),
        blank=True,
        help_text=_("Information about who to contact regarding the event."),
    )

    # Promote tab
    short_title = models.CharField(
        max_length=50,
        verbose_name=_("short title"),
        help_text=_(
            "A short title for the event. This will be used in the event listings."
        ),
    )

    # DataLayerMixin overrides
    gtm_content_group = "What's On"

    class Meta:
        verbose_name = _("event page")

    content_panels = BasePageWithIntro.content_panels + [
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
                FieldPanel("video_conference_info"),
            ],
            heading=_("Venue information"),
        ),
        MultiFieldPanel(
            [
                FieldPanel("registration_url", read_only=True),
                FieldPanel("registration_cost", read_only=True),
                FieldPanel("registration_info"),
                FieldPanel("contact_info"),
            ],
            heading=_("Booking information"),
        ),
    ]

    @cached_property
    def primary_access_type(self):
        """
        Returns the primary access type for the event.
        """
        if primary_access := self.event_access_types.first():
            return primary_access.access_type

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


class EventFilterForm(forms.Form):
    date = forms.DateField(
        label="Choose a date",
        required=False,
        widget=forms.DateInput(attrs={"type": "date", "class": "filters__date"}),
    )

    category = forms.ModelChoiceField(
        widget=forms.RadioSelect(attrs={"class": "filters__radio"}),
        queryset=EventType.objects.all(),
        required=False,
        label="What",
    )

    online = forms.BooleanField(label="Online", required=False, widget=forms.CheckboxInput(attrs={"class": "filters__toggle-input"}))

    family_friendly = forms.BooleanField(label="Family friendly", required=False, widget=forms.CheckboxInput(attrs={"class": "filters__toggle-input"}))