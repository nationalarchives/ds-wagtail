from django.core.exceptions import ValidationError
from django.db import models
from django.utils.functional import cached_property
from django.utils.translation import gettext_lazy as _

from modelcluster.fields import ParentalKey
from wagtail.admin.panels import FieldPanel, InlinePanel, MultiFieldPanel
from wagtail.fields import RichTextField, StreamField
from wagtail.images import get_image_model_string
from wagtail.models import Orderable
from wagtail.search import index
from wagtail.snippets.models import register_snippet

from etna.articles.models import ArticleTagMixin
from etna.collections.models import TopicalPageMixin
from etna.core.models import BasePageWithIntro

from .blocks import EventPageBlock


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

    access_type = models.ForeignKey(
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
            .order_by("eventpage__event_start_date")
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

    body = StreamField(
        EventPageBlock,
        blank=True,
        null=True,
        help_text="Add content for this page",
        use_json_field=True,
    )

    # Event information
    event_type = models.ForeignKey(
        EventType,
        null=True,
        blank=False,
        on_delete=models.SET_NULL,
        related_name="+",
    )

    event_start_date = models.DateTimeField(
        verbose_name=_("event start date"),
        null=True,
        blank=False,
        help_text=_("The date and time the event starts."),
    )

    event_end_date = models.DateTimeField(
        verbose_name=_("event end date"),
        null=True,
        blank=False,
        help_text=_("The date and time the event ends."),
    )

    event_registration_info = RichTextField(
        verbose_name=_("event registration info"),
        null=True,
        blank=True,
        help_text=_("Information about how to register for the event."),
    )

    event_contact_info = RichTextField(
        verbose_name=_("event contact info"),
        null=True,
        blank=True,
        help_text=_("Information about who to contact for the event."),
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
        FieldPanel("body"),
        MultiFieldPanel(
            [
                FieldPanel("event_type"),
                FieldPanel("event_start_date"),
                FieldPanel("event_end_date"),
                FieldPanel("event_registration_info"),
                FieldPanel("event_contact_info"),
            ],
            heading=_("Event information"),
        ),
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
    ]

    def clean(self):
        """
        Validate that the event end date is after the event start date.
        """
        if self.event_start_date and self.event_end_date:
            if self.event_start_date > self.event_end_date:
                raise ValidationError(
                    {
                        "event_end_date": _(
                            "The event end date must be after the event start date."
                        )
                    }
                )

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
