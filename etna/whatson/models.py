from django.conf import settings
from django.core.exceptions import ValidationError
from django.db import models
from django.utils import timezone
from django.utils.functional import cached_property
from django.utils.translation import gettext_lazy as _
from modelcluster.fields import ParentalKey
from rest_framework import serializers
from wagtail import blocks
from wagtail.admin.panels import (
    FieldPanel,
    FieldRowPanel,
    InlinePanel,
    MultiFieldPanel,
    ObjectList,
    TabbedInterface,
    TitleFieldPanel,
)
from wagtail.api import APIField
from wagtail.fields import RichTextField, StreamField
from wagtail.images import get_image_model_string
from wagtail.models import Orderable
from wagtail.search import index
from wagtail.snippets.models import register_snippet

from etna.articles.models import ArticleTagMixin
from etna.collections.models import TopicalPageMixin
from etna.core.blocks import (
    ContentImageBlock,
    FeaturedExternalLinkBlock,
    FeaturedPagesBlock,
    ImageGalleryBlock,
    MixedMediaBlock,
    ReviewBlock,
    ShopCollectionBlock,
    SimplifiedAccordionBlock,
)
from etna.core.models import (
    AccentColourMixin,
    BasePageWithRequiredIntro,
    HeroLayoutMixin,
    HeroStyleMixin,
    LocationSerializer,
    RequiredHeroImageMixin,
)
from etna.core.serializers import (
    DefaultPageSerializer,
    ImageSerializer,
    RichTextSerializer,
)

from .blocks import ExhibitionPageStreamBlock

class SeriesTag(models.Model):
    """
    This model is used to tag series pages.
    """

    page = ParentalKey(
        "wagtailcore.Page",
        on_delete=models.CASCADE,
        related_name="page_series_tags",
    )

    series = models.ForeignKey(
        "whatson.WhatsOnSeriesPage",
        on_delete=models.CASCADE,
        related_name="series_pages",
        verbose_name=_("series"),
        help_text=_("The series to include the page in."),
        null=False,
        blank=False,
    )
    
    class Meta:
        verbose_name = _("series")
        verbose_name_plural = _("series")

    def __str__(self):
        return f"{self.page.title}: {self.series.title}"

class WhatsOnSeriesPage(BasePageWithRequiredIntro):
    """WhatsOnSeriesPage

    A page for creating a series/grouping of events.
    """

    # DataLayerMixin overrides
    gtm_content_group = "What's On"

    class Meta:
        verbose_name = _("What's On series page")

    parent_page_types = [
        "whatson.WhatsOnPage",
    ]
    subpage_types = []

    content_panels = BasePageWithRequiredIntro.content_panels + [
        
    ]

    api_fields = (
        BasePageWithRequiredIntro.api_fields
    )

@register_snippet
class EventCategory(models.Model):
    """
    This snippet model is used so that editors can add event categories,
    which we use via the event_category ForeignKey to add event categories
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


class EventCategorySerializer(serializers.ModelSerializer):
    """Serializer for the EventCategory model."""

    class Meta:
        model = EventCategory
        fields = ("name", "slug")


class CategorySelection(models.Model):
    page = ParentalKey(
        "wagtailcore.Page",
        on_delete=models.CASCADE,
        related_name="category_pages",
    )
    category = models.ForeignKey(
        "whatson.EventCategory",
        on_delete=models.CASCADE,
        related_name="selected_category",
        verbose_name=_("category"),
        help_text=_("The category of events to display on the Category page."),
        null=False,
        blank=False,
    )


class WhatsOnCategoryPage(BasePageWithRequiredIntro):
    """WhatsOnCategoryPage

    A page for displaying a category of events.
    """

    # DataLayerMixin overrides
    gtm_content_group = "What's On"

    class Meta:
        verbose_name = _("What's On category page")

    parent_page_types = [
        "whatson.WhatsOnPage",
    ]
    subpage_types = []

    content_panels = BasePageWithRequiredIntro.content_panels + [
        InlinePanel(
            "category_pages",
            heading=_("Category selection"),
        ),
    ]

    @cached_property
    def categories(self) -> tuple:
        """
        Returns the categories selected for this category page.
        """
        return tuple(
            item.category
            for item in self.category_pages.select_related("category")
        )

    api_fields = BasePageWithRequiredIntro.api_fields + [
        APIField("categories", serializer=EventCategorySerializer(many=True)),
    ]


class WhatsOnEventsPage(BasePageWithRequiredIntro):
    pass

    max_count = 1

    parent_page_types = [
        "whatson.WhatsOnPage",
    ]
    subpage_types = [
        "whatson.EventPage"
    ]

class WhatsOnExhibitionsPage(BasePageWithRequiredIntro):
    pass

    max_count = 1



class WhatsOnPage(BasePageWithRequiredIntro):
    """WhatsOnPage

    A page for listing events.
    """

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
        "whatson.WhatsOnSeriesPage",
        "whatson.WhatsOnCategoryPage",
    ]

    max_count = 1

    content_panels = BasePageWithRequiredIntro.content_panels + [
    ]

    api_fields = (
        BasePageWithRequiredIntro.api_fields
        + [
            APIField("latest_listings"),
        ]
    )


class EventSpeaker(Orderable):
    """
    This model is used to add speaker information to event pages.
    """

    page = ParentalKey(
        "wagtailcore.Page",
        on_delete=models.CASCADE,
        related_name="speakers",
    )

    person_page = models.ForeignKey(
        "people.PersonPage",
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="+",
    )

    name = models.CharField(
        max_length=100,
        verbose_name=_("name"),
        help_text=_("The name of the speaker."),
        blank=True,
    )

    role = models.CharField(
        max_length=200,
        verbose_name=_("role"),
        help_text=_("The role of the speaker."),
        blank=True,
    )

    biography = RichTextField(
        verbose_name=_("biography"),
        help_text=_("A short biography of the speaker."),
        blank=True,
        features=settings.INLINE_RICH_TEXT_FEATURES,
    )

    image = models.ForeignKey(
        get_image_model_string(),
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="+",
    )

    panels = [
        FieldPanel("person_page"),
        FieldPanel("name"),
        FieldPanel("role"),
        FieldPanel("biography"),
        FieldPanel("image"),
    ]


class SpeakerSerializer(serializers.ModelSerializer):
    """Serializer for the EventSpeaker model."""

    biography = RichTextSerializer()
    image = ImageSerializer()
    person_page = DefaultPageSerializer()

    class Meta:
        model = EventSpeaker
        fields = ("name", "role", "biography", "image", "person_page")


class EventSession(models.Model):
    """
    This model is used to add sessions to an event
    e.g. 28th September @ 9:00, 29th September @ 10:30, 30th September @ 12:00.
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


class SessionSerializer(serializers.ModelSerializer):
    """Serializer for the EventSession model."""

    class Meta:
        model = EventSession
        fields = ("start", "end")


class EventPage(RequiredHeroImageMixin, BasePageWithRequiredIntro):
    """EventPage

    A page for an event.
    """

    # Event information
    event_category = models.ForeignKey(
        EventCategory,
        null=True,
        blank=False,
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

    booking_details = RichTextField(
        max_length=40,
        null=True,
        blank=True,
        verbose_name=_("booking details"),
        help_text=_("Information about how to book tickets for the exhibition."),
        features=["link"],
    )

    min_price = models.FloatField(
        verbose_name=_("minimum price"),
        default=0,
    )

    max_price = models.FloatField(
        verbose_name=_("maximum price"),
        default=0,
    )

    location = models.ForeignKey(
        "core.Location",
        null=True,
        blank=False,
        on_delete=models.SET_NULL,
        related_name="+",
        verbose_name=_("location"),
        help_text=_("The location of the event."),
    )

    booking_link = models.URLField(
        null=True,
        blank=True,
        help_text="Link to booking page",
        verbose_name="Booking link",
    )

    # DataLayerMixin overrides
    gtm_content_group = "What's On"

    class Meta:
        verbose_name = _("event page")

    content_panels = (
        BasePageWithRequiredIntro.content_panels
        + RequiredHeroImageMixin.content_panels
        + [
            MultiFieldPanel(
                [
                    FieldPanel("description"),
                ],
                heading=_("Event information"),
            ),
        ]
    )

    key_details_panels = [
        FieldPanel("event_category"),
        MultiFieldPanel(
            [
                FieldPanel("booking_link"),
                FieldPanel("booking_details"),
                FieldRowPanel(
                    [
                        FieldPanel("min_price"),
                        FieldPanel("max_price"),
                    ],
                ),
            ],
            heading=_("Price details"),
        ),
        MultiFieldPanel(
            [
                FieldRowPanel(
                    [
                        FieldPanel("start_date", read_only=True),
                        FieldPanel("end_date", read_only=True),
                    ],
                ),
                InlinePanel(
                    "sessions",
                    heading=_("Sessions"),
                    min_num=1,
                ),
            ],
            heading=_("Date details"),
        ),
        FieldPanel("location"),
        MultiFieldPanel(
            [
                FieldPanel("audience_heading"),
                FieldPanel("audience_detail"),
            ],
            heading=_("Audience details"),
        ),
        InlinePanel(
            "speakers",
            heading=_("Speaker information"),
            help_text=_(
                "If the event has more than one speaker, please add these in order of relevance from most to least."
            ),
        ),
    ]

    promote_panels = (
        BasePageWithRequiredIntro.promote_panels
        + [
            InlinePanel(
                "page_series_tags",
                heading=_("Series"),
                max_num=3,
            ),
        ]
    )

    @cached_property
    def series(self):
        """
        Returns the series this event page belongs to, if any.
        """
        return [tag.series for tag in self.page_series_tags.all() if tag.series]

    api_fields = (
        BasePageWithRequiredIntro.api_fields
        + RequiredHeroImageMixin.api_fields
        + [
            APIField("location", serializer=LocationSerializer()),
            APIField("event_category", serializer=EventCategorySerializer()),
            APIField("start_date"),
            APIField("end_date"),
            APIField("description", serializer=RichTextSerializer()),
            APIField("audience_heading"),
            APIField("audience_detail"),
            APIField("booking_details", serializer=RichTextSerializer()),
            APIField("min_price"),
            APIField("max_price"),
            APIField("price_range"),
            APIField("booking_link"),
            APIField("event_status"),
            APIField("date_time_range"),
            APIField("speakers", serializer=SpeakerSerializer(many=True)),
            APIField("sessions", serializer=SessionSerializer(many=True)),
            APIField("series", serializer=DefaultPageSerializer(many=True)),
        ]
    )

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

    edit_handler = TabbedInterface(
        [
            ObjectList(content_panels, heading="Content"),
            ObjectList(key_details_panels, heading="Key details"),
            ObjectList(promote_panels, heading="Promote"),
            ObjectList(BasePageWithRequiredIntro.settings_panels, heading="Settings"),
        ]
    )

    parent_page_types = [
        "whatson.WhatsOnPage",
    ]
    subpage_types = []


class ExhibitionPage(
    ArticleTagMixin,
    AccentColourMixin,
    HeroStyleMixin,
    HeroLayoutMixin,
    RequiredHeroImageMixin,
    TopicalPageMixin,
    BasePageWithRequiredIntro,
):
    """ExhibitionPage

    An event where editors can create exhibitions. Exhibitions do not come
    from Eventbrite - they are internal TNA exhibitions.
    """

    # Hero section
    subtitle = models.CharField(
        max_length=120,
        verbose_name=_("subtitle"),
        help_text=_("A subtitle for the event."),
    )

    # Key details section
    start_date = models.DateField(
        verbose_name=_("start date"),
        null=True,
        blank=True,
    )

    end_date = models.DateField(
        verbose_name=_("end date"),
        null=True,
        blank=True,
    )

    exclude_days = models.BooleanField(
        verbose_name=_("exclude days"),
        default=False,
        help_text=_(
            "Check this box to show only the month and year on the exhibition."
        ),
    )

    price = models.FloatField(
        verbose_name=_("price"),
        default=0,
    )

    booking_details = RichTextField(
        max_length=40,
        null=True,
        verbose_name=_("booking details"),
        help_text=_("Information about how to book tickets for the exhibition."),
        features=["link"],
    )

    open_days = models.CharField(
        max_length=255,
        verbose_name=_("open days"),
        blank=True,
        help_text=_("The days the exhibition is open, e.g. Tuesday to Sunday."),
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

    location_space_name = models.CharField(
        max_length=40,
        verbose_name=_("location space name"),
        null=True,
        help_text=_("The location of the exhibition within the venue."),
    )

    location_address = RichTextField(
        verbose_name=_("location address"),
        null=True,
        blank=True,
        help_text=_("Leave blank to default to TNA address."),
        features=["link"],
    )

    # Body section
    intro_title = models.CharField(
        max_length=100,
        verbose_name=_("intro title"),
        blank=True,
        help_text=_(
            "Only used in jump links. Does not appear on page. Leave blank to default to 'About [Page title]'."
        ),
    )

    body = StreamField(ExhibitionPageStreamBlock, blank=True, null=True)

    exhibition_highlights_title = models.CharField(
        max_length=100,
        verbose_name=_("exhibition highlights title"),
        blank=True,
        help_text=_("Leave blank to default to 'Exhibition highlights'."),
    )

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

    video_title = models.CharField(
        max_length=100,
        verbose_name=_("video title"),
        blank=True,
        help_text=_("The title of the video section."),
    )

    video = StreamField(
        MixedMediaBlock(
            block_counts={"youtube": {"max_num": 1}, "media": {"max_num": 1}}
        ),
        blank=True,
        max_num=1,
    )

    # Related content section
    related_pages_title = models.CharField(
        max_length=255,
        blank=True,
        help_text=_("The title to display for the related content section."),
    )

    related_pages_description = RichTextField(
        blank=True,
        help_text=_("The description to display for the related content section."),
        features=settings.INLINE_RICH_TEXT_FEATURES,
    )

    featured_page = models.ForeignKey(
        "wagtailcore.Page",
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="+",
    )

    related_pages = StreamField(FeaturedPagesBlock(), blank=True, null=True)

    event_title = models.CharField(
        max_length=100,
        verbose_name=_("event title"),
        help_text=_("The title of the events section."),
        default="Exhibition events",
        blank=True,
        null=True,
    )

    event_description = RichTextField(
        blank=True,
        help_text=_("The description to display for the events section."),
        features=settings.INLINE_RICH_TEXT_FEATURES,
    )

    event_links = StreamField(
        [
            (
                "event_links",
                blocks.ListBlock(FeaturedExternalLinkBlock(), max_num=2),
            )
        ],
        max_num=1,
        null=True,
        blank=True,
    )

    shop = StreamField(
        [("shop", ShopCollectionBlock())],
        blank=True,
        max_num=1,
    )

    # Plan your visit section
    plan_your_visit_title = models.CharField(
        max_length=100,
        blank=True,
        help_text=_("Leave blank to default to 'Plan your visit'."),
    )

    plan_your_visit_image = StreamField(
        [("image", ContentImageBlock())],
        blank=True,
        null=True,
        max_num=1,
    )

    plan_your_visit = StreamField(
        [("plan_your_visit", blocks.ListBlock(SimplifiedAccordionBlock()))],
        blank=True,
        max_num=1,
    )

    # DataLayerMixin overrides
    gtm_content_group = "What's On"

    @cached_property
    def type_label(cls) -> str:
        """
        Overrides the type_label method from BasePage, to return the correct
        type label for the exhibition page.
        """
        if cls.end_date < timezone.now().date():
            return "Past exhibition"
        return "Exhibition"

    class Meta:
        verbose_name = _("exhibition page")
        verbose_name_plural = _("exhibition pages")
        verbose_name_public = _("exhibition")

    content_panels = [
        TitleFieldPanel("title"),
        FieldPanel("subtitle"),
        MultiFieldPanel(
            [
                FieldPanel("hero_image"),
                FieldPanel("hero_image_caption"),
                FieldPanel("hero_style"),
                FieldPanel("hero_layout"),
            ],
            heading=_("Hero section"),
        ),
        MultiFieldPanel(
            [
                FieldPanel("intro_title"),
                FieldPanel("intro"),
                FieldPanel("body"),
                FieldPanel("exhibition_highlights_title"),
                FieldPanel("exhibition_highlights"),
                FieldPanel("review"),
                FieldPanel("video_title"),
                FieldPanel("video"),
            ],
            heading=_("Content"),
        ),
        MultiFieldPanel(
            [
                FieldPanel("related_pages_title"),
                FieldPanel("related_pages_description"),
                FieldPanel("featured_page"),
                FieldPanel("related_pages"),
                FieldPanel("event_title"),
                FieldPanel("event_description"),
                FieldPanel("event_links"),
                FieldPanel("shop"),
            ],
            heading=_("Related content"),
        ),
        MultiFieldPanel(
            [
                FieldPanel("plan_your_visit_title"),
                FieldPanel("plan_your_visit_image"),
                FieldPanel("plan_your_visit"),
            ],
            heading=_("Plan your visit"),
        ),
    ]

    key_details_panels = [
        MultiFieldPanel(
            [
                FieldRowPanel(
                    [
                        FieldPanel("start_date"),
                        FieldPanel("end_date"),
                    ],
                ),
                FieldPanel("exclude_days"),
            ],
            heading=_("Date details"),
        ),
        MultiFieldPanel(
            [
                FieldPanel("price"),
                FieldPanel("booking_details"),
            ],
            heading=_("Price details"),
        ),
        FieldPanel("open_days"),
        MultiFieldPanel(
            [
                FieldPanel("audience_heading"),
                FieldPanel("audience_detail"),
            ],
            heading=_("Audience details"),
        ),
        MultiFieldPanel(
            [
                FieldPanel("location_space_name"),
                FieldPanel("location_address"),
            ],
            heading=_("Location details"),
        ),
    ]

    design_panels = [
        FieldPanel("accent_colour"),
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
        + RequiredHeroImageMixin.api_fields
        + HeroStyleMixin.api_fields
        + HeroLayoutMixin.api_fields
        + AccentColourMixin.api_fields
        + [
            APIField("subtitle"),
            APIField("start_date"),
            APIField("end_date"),
            APIField("exclude_days"),
            APIField("price"),
            APIField("open_days"),
            APIField("booking_details", serializer=RichTextSerializer()),
            APIField("audience_heading"),
            APIField("audience_detail"),
            APIField("location_space_name"),
            APIField("location_address", serializer=RichTextSerializer()),
            APIField("intro_title"),
            APIField("body"),
            APIField("exhibition_highlights_title"),
            APIField("exhibition_highlights"),
            APIField("review"),
            APIField("video_title"),
            APIField("video"),
            APIField("related_pages_title"),
            APIField("related_pages_description", serializer=RichTextSerializer()),
            APIField("featured_page", serializer=DefaultPageSerializer()),
            APIField("related_pages"),
            APIField("event_title"),
            APIField("event_description", serializer=RichTextSerializer()),
            APIField("event_links"),
            APIField("shop"),
            APIField("plan_your_visit_title"),
            APIField("plan_your_visit_image"),
            APIField("plan_your_visit"),
        ]
        + TopicalPageMixin.api_fields
        + ArticleTagMixin.api_fields
    )

    edit_handler = TabbedInterface(
        [
            ObjectList(content_panels, heading="Content"),
            ObjectList(key_details_panels, heading="Key details"),
            ObjectList(design_panels, heading="Design"),
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
        "home.HomePage",
    ]
    subpage_types = []

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
        if self.video and not self.video_title:
            raise ValidationError(
                {
                    "video_title": _(
                        "The video title is required if a video is added."
                    ),
                }
            )
        return super().clean()
