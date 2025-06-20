import datetime

from django.conf import settings
from django.core.exceptions import ValidationError
from django.db import models
from django.utils import timezone
from django.utils.functional import cached_property
from django.utils.translation import gettext_lazy as _
from modelcluster.fields import ParentalKey
from wagtail import blocks
from wagtail.admin.panels import (
    FieldPanel,
    FieldRowPanel,
    InlinePanel,
    MultiFieldPanel,
    ObjectList,
    PageChooserPanel,
    TabbedInterface,
    TitleFieldPanel,
)
from wagtail.api import APIField
from wagtail.fields import RichTextField, StreamField
from wagtail.images import get_image_model_string
from wagtail.models import Orderable
from wagtail.snippets.models import register_snippet

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
    ContentWarningMixin,
    HeroLayoutMixin,
    HeroStyleMixin,
    LocationSerializer,
    RequiredHeroImageMixin,
)
from etna.core.serializers import (
    DefaultPageSerializer,
    RichTextSerializer,
)

from .blocks import ExhibitionPageStreamBlock
from .serializers import (
    EventCategorySerializer,
    SessionSerializer,
    SpeakerSerializer,
    WhatsOnPageSelectionSerializer,
)


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
    """
    A page for creating a series/grouping of events.
    """

    featured_page = models.ForeignKey(
        "wagtailcore.Page",
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="+",
        verbose_name=_("featured page"),
        help_text=_("The page to feature on the series page."),
    )

    class Meta:
        verbose_name = _("What's On series page")

    parent_page_types = [
        "whatson.WhatsOnPage",
    ]

    subpage_types = []

    @cached_property
    def related_page_pks(self) -> tuple[int]:
        return tuple(self.series_pages.values_list("page_id", flat=True))

    @cached_property
    def event_listings(self) -> list:
        """
        Returns a list of event pages that belong to this series.
        """
        return [
            page
            for page in EventPage.objects.live()
            .public()
            .filter(
                pk__in=self.related_page_pks,
            )
            .order_by("start_date")
            if page.end_date >= timezone.now()
        ]

    @cached_property
    def exhibition_listings(self) -> list:
        """
        Returns a list of exhibition and display pages that belong to this series.
        """
        page_list = []

        for page_type in [ExhibitionPage, DisplayPage]:
            page_list.extend(
                page_type.objects.exclude(pk=self.featured_page_id)
                .filter(pk__in=self.related_page_pks)
                .filter(end_date__gt=timezone.now())
                .live()
                .public()
                .order_by("start_date")
            )

        return page_list

    @cached_property
    def latest_listings(self) -> list:
        """
        Returns a list of the latest event pages that belong to the categories
        selected for this category page.
        """

        def get_start_date(obj):
            value = obj.start_date
            if isinstance(value, datetime.date) and not isinstance(
                value, datetime.datetime
            ):
                return datetime.datetime.combine(
                    value, datetime.time.min, tzinfo=timezone.get_current_timezone()
                )
            return value

        return sorted(
            self.event_listings + self.exhibition_listings,
            key=get_start_date,
            reverse=True,
        )[:3]

    content_panels = BasePageWithRequiredIntro.content_panels + [
        PageChooserPanel(
            "featured_page",
            page_type=[
                "whatson.EventPage",
                "whatson.ExhibitionPage",
                "whatson.DisplayPage",
            ],
        )
    ]

    default_api_fields = BasePageWithRequiredIntro.default_api_fields + [
        APIField("latest_listings", serializer=DefaultPageSerializer(many=True)),
    ]

    api_fields = BasePageWithRequiredIntro.api_fields + [
        APIField("event_listings", serializer=DefaultPageSerializer(many=True)),
        APIField("exhibition_listings", serializer=DefaultPageSerializer(many=True)),
    ]


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
        verbose_name = _("event category")
        verbose_name_plural = _("event categories")

    def __str__(self):
        return self.name


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
    """
    A page for displaying a category of events.
    """

    featured_page = models.ForeignKey(
        "wagtailcore.Page",
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="+",
        verbose_name=_("featured page"),
        help_text=_("The page to feature on the category page."),
    )

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
        PageChooserPanel(
            "featured_page",
            page_type="whatson.EventPage",
        ),
    ]

    @cached_property
    def categories(self) -> tuple:
        """
        Returns the categories selected for this category page.
        """
        return tuple(
            item.category for item in self.category_pages.select_related("category")
        )

    @cached_property
    def event_listings(self) -> list:
        """
        Returns a list of event pages that belong to the categories selected
        for this category page.
        """
        return [
            page
            for page in EventPage.objects.live()
            .public()
            .filter(
                event_category__in=self.categories,
            )
            .order_by("start_date")
            if page.end_date >= timezone.now()
        ]

    @cached_property
    def latest_listings(self) -> list:
        """
        Returns a list of the latest event pages that belong to the categories
        selected for this category page.
        """
        return self.event_listings[:3]

    default_api_fields = BasePageWithRequiredIntro.default_api_fields + [
        APIField("latest_listings", serializer=DefaultPageSerializer(many=True)),
    ]

    api_fields = BasePageWithRequiredIntro.api_fields + [
        APIField("featured_page", serializer=DefaultPageSerializer()),
        APIField("categories", serializer=EventCategorySerializer(many=True)),
        APIField(
            "event_listings",
            serializer=DefaultPageSerializer(many=True),
        ),
    ]


class EventsListingPage(BasePageWithRequiredIntro):
    """
    A page for listing/storing all events.
    """

    max_count = 1

    parent_page_types = [
        "whatson.WhatsOnPage",
    ]
    subpage_types = ["whatson.EventPage"]

    @cached_property
    def event_listings(self) -> list:
        """
        Returns a list of event pages.
        """
        return (
            EventPage.objects.live()
            .public()
            .filter(
                end_date__gte=timezone.now(),
            )
            .order_by("start_date")
        )

    @cached_property
    def latest_listings(self) -> list:
        """
        Returns a list of the latest event pages.
        """
        return self.event_listings[:3]

    default_api_fields = BasePageWithRequiredIntro.default_api_fields + [
        APIField("latest_listings", serializer=DefaultPageSerializer(many=True)),
    ]

    api_fields = BasePageWithRequiredIntro.api_fields + [
        APIField(
            "event_listings",
            serializer=DefaultPageSerializer(many=True),
        ),
    ]


class ExhibitionsListingPage(BasePageWithRequiredIntro):
    """
    A page for listing/storing all displays/exhibitions.
    """

    @cached_property
    def exhibition_listings(self) -> list:
        """
        Returns a list of exhibition and display pages.
        """
        children = [
            page
            for page in self.get_children().live().public().specific()
            if isinstance(page, (ExhibitionPage, DisplayPage))
            and page.end_date >= timezone.now().date()
        ]
        return sorted(children, key=lambda x: x.start_date)

    @cached_property
    def latest_listings(self) -> list:
        """
        Returns a list of the latest exhibition and display pages.
        """
        return self.exhibition_listings[:3]

    @cached_property
    def past_exhibition_listings(self) -> list:
        """
        Returns a list of past exhibition and display pages.
        """
        children = [
            page
            for page in self.get_children().live().public().specific()
            if isinstance(page, (ExhibitionPage, DisplayPage))
            and page.end_date < timezone.now().date()
        ]
        return sorted(children, key=lambda x: x.start_date)

    max_count = 1

    parent_page_types = [
        "whatson.WhatsOnPage",
    ]
    subpage_types = ["whatson.ExhibitionPage", "whatson.DisplayPage"]

    default_api_fields = BasePageWithRequiredIntro.default_api_fields + [
        APIField(
            "latest_listings",
            serializer=DefaultPageSerializer(many=True),
        ),
    ]

    api_fields = BasePageWithRequiredIntro.api_fields + [
        APIField(
            "exhibition_listings",
            serializer=DefaultPageSerializer(many=True),
        ),
        APIField(
            "past_exhibition_listings",
            serializer=DefaultPageSerializer(many=True),
        ),
    ]


class WhatsOnPageSelection(models.Model):
    """
    This model is used to select a page to display on the What's On page.
    """

    page = ParentalKey(
        "wagtailcore.Page",
        on_delete=models.CASCADE,
        related_name="whats_on_page_selections",
    )

    featured_page = models.ForeignKey(
        "wagtailcore.Page",
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="+",
        verbose_name=_("featured page"),
        help_text=_("The page to feature on the What's On page."),
    )

    selected_page = models.ForeignKey(
        "wagtailcore.Page",
        on_delete=models.CASCADE,
        related_name="+",
        verbose_name=_("selected page"),
        help_text=_("The page to display on the What's On page."),
    )

    panels = [
        PageChooserPanel(
            "featured_page",
            page_type=[
                "whatson.EventPage",
                "whatson.ExhibitionPage",
                "whatson.DisplayPage",
            ],
        ),
        PageChooserPanel(
            "selected_page",
            page_type=[
                "whatson.ExhibitionsListingPage",
                "whatson.EventsListingPage",
                "whatson.WhatsOnSeriesPage",
                "whatson.WhatsOnCategoryPage",
            ],
        ),
    ]

    class Meta:
        verbose_name = _("selection")


class WhatsOnPage(BasePageWithRequiredIntro):
    """
    A page for listing events.
    """

    class Meta:
        verbose_name = _("What's On page")

    parent_page_types = [
        "home.HomePage",
    ]
    subpage_types = [
        "whatson.EventsListingPage",
        "whatson.ExhibitionsListingPage",
        "whatson.WhatsOnSeriesPage",
        "whatson.WhatsOnCategoryPage",
    ]

    max_count = 1

    content_panels = BasePageWithRequiredIntro.content_panels + [
        InlinePanel(
            "whats_on_page_selections",
            heading=_("Page selections"),
            help_text=_("Select pages to display on the What's On page."),
        ),
    ]

    api_fields = BasePageWithRequiredIntro.api_fields + [
        APIField(
            "whats_on_page_selections",
            serializer=WhatsOnPageSelectionSerializer(many=True),
        ),
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

    def clean(self):
        if not (self.name and self.role) and not self.person_page:
            raise ValidationError(
                _(
                    "You must provide either a person's name and role or a person page for the speaker."
                )
            )
        if (
            (self.person_page and self.name)
            or (self.person_page and self.role)
            or (self.person_page and self.image)
        ):
            raise ValidationError(
                _(
                    "You cannot provide both a person's details and a person page for the speaker."
                )
            )
        return super().clean()


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

    sold_out = models.BooleanField(
        verbose_name=_("sold out"),
        default=False,
        help_text=_("Check this box if the session is sold out."),
    )

    panels = [
        FieldPanel("start"),
        FieldPanel("end"),
        FieldPanel("sold_out"),
    ]

    class Meta:
        verbose_name = _("session")
        verbose_name_plural = _("sessions")
        ordering = ["start"]


class EventPage(RequiredHeroImageMixin, ContentWarningMixin, BasePageWithRequiredIntro):
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
        help_text=_("Information about how to book tickets for the event."),
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

    event_highlights_title = models.CharField(
        max_length=100,
        verbose_name=_("event highlights title"),
        blank=True,
        help_text=_("Leave blank to default to 'Event highlights'."),
    )

    event_highlights = StreamField(
        [("event_highlights", ImageGalleryBlock())],
        blank=True,
        max_num=1,
    )

    class Meta:
        verbose_name = _("event page")

    content_panels = (
        BasePageWithRequiredIntro.content_panels
        + RequiredHeroImageMixin.content_panels
        + ContentWarningMixin.content_panels
        + [
            MultiFieldPanel(
                [
                    FieldPanel("description"),
                ],
                heading=_("Event information"),
            ),
            MultiFieldPanel(
                [
                    FieldPanel("event_highlights_title"),
                    FieldPanel("event_highlights"),
                ],
                heading=_("Event highlights"),
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
                    help_text=_(
                        "These dates are automatically set based on the sessions added."
                    ),
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

    promote_panels = BasePageWithRequiredIntro.promote_panels + [
        InlinePanel(
            "page_series_tags",
            heading=_("Series"),
            max_num=3,
        ),
    ]

    default_api_fields = BasePageWithRequiredIntro.default_api_fields + [
        APIField("start_date"),
        APIField("end_date"),
        APIField("price_range"),
        APIField("short_location"),
    ]

    api_fields = (
        BasePageWithRequiredIntro.api_fields
        + RequiredHeroImageMixin.api_fields
        + ContentWarningMixin.api_fields
        + [
            APIField("short_location"),
            APIField("location", serializer=LocationSerializer()),
            APIField("event_category", serializer=EventCategorySerializer()),
            APIField("start_date"),
            APIField("end_date"),
            APIField("description", serializer=RichTextSerializer()),
            APIField("event_highlights_title"),
            APIField("event_highlights"),
            APIField("audience_heading"),
            APIField("audience_detail"),
            APIField("booking_details", serializer=RichTextSerializer()),
            APIField("sold_out"),
            APIField("min_price"),
            APIField("max_price"),
            APIField("price_range"),
            APIField("booking_link"),
            APIField("speakers", serializer=SpeakerSerializer(many=True)),
            APIField("sessions", serializer=SessionSerializer(many=True)),
            APIField("series", serializer=DefaultPageSerializer(many=True)),
        ]
    )

    @cached_property
    def short_location(self) -> str:
        """
        Returns a short version of the location name.
        """
        if location := self.location:
            if location.online:
                return "Online"
            elif location.at_tna:
                return "At The National Archives, Kew"
            else:
                return location.address_line_1 or location.space_name or "In-person"

    @cached_property
    def series(self):
        """
        Returns the series this event page belongs to, if any.
        """
        return [tag.series for tag in self.page_series_tags.all() if tag.series]

    @cached_property
    def type_label(cls) -> str:
        """
        Overrides the type_label method from BasePage, to return the correct
        type label for the event page which will be the event category name.
        """
        if cls.event_category:
            return cls.event_category.name
        return "Event"

    @cached_property
    def price_range(self) -> str:
        """
        Returns the price range for the event.
        """
        if self.max_price == 0:
            return "Free"
        elif self.min_price == self.max_price:
            return f"£{self.min_price:.2f}"
        else:
            if self.min_price == 0:
                return f"Free - £{self.max_price:.2f}"
            return f"£{self.min_price:.2f} - {self.max_price:.2f}"

    @cached_property
    def sold_out(self) -> bool:
        """
        Returns True if all sessions of an event is sold out, otherwise False.
        """
        return all(session.sold_out for session in self.sessions.all())

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
        "whatson.EventsListingPage",
    ]
    subpage_types = []


class DisplayPage(
    RequiredHeroImageMixin,
    ContentWarningMixin,
    BasePageWithRequiredIntro,
):
    """
    A page where editors can create displays. Displays do not come
    from Eventbrite - they are internal TNA displays.
    """

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
        help_text=_("Check this box to show only the month and year on the display."),
    )

    price = models.FloatField(
        verbose_name=_("price"),
        default=0,
    )

    booking_details = RichTextField(
        max_length=40,
        null=True,
        verbose_name=_("booking details"),
        help_text=_("Information about how to book tickets for the display."),
        features=["link"],
    )

    open_days = models.CharField(
        max_length=255,
        verbose_name=_("open days"),
        blank=True,
        help_text=_("The days the display is open, e.g. Tuesday to Sunday."),
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

    location = models.ForeignKey(
        "core.Location",
        null=True,
        blank=False,
        on_delete=models.SET_NULL,
        related_name="+",
        verbose_name=_("location"),
        help_text=_("The location of the display."),
    )

    # Body section
    body = StreamField(ExhibitionPageStreamBlock, blank=True, null=True)

    display_highlights_title = models.CharField(
        max_length=100,
        verbose_name=_("display highlights title"),
        blank=True,
        help_text=_("Leave blank to default to 'Display highlights'."),
    )

    display_highlights = StreamField(
        [("display_highlights", ImageGalleryBlock())],
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

    shop = StreamField(
        [("shop", ShopCollectionBlock())],
        blank=True,
        max_num=1,
    )

    @cached_property
    def type_label(cls) -> str:
        """
        Overrides the type_label method from BasePage, to return the correct
        type label for the display page.
        """
        if cls.end_date:
            if cls.end_date < timezone.now().date():
                return "Past display"
        return "Display"

    @cached_property
    def short_location(self) -> str:
        """
        Returns a short version of the location name.
        """
        if location := self.location:
            if location.online:
                return "Online"
            elif location.at_tna:
                return "At The National Archives, Kew"
            else:
                return location.address_line_1 or location.space_name or "In-person"

    class Meta:
        verbose_name = _("display page")
        verbose_name_plural = _("display pages")
        verbose_name_public = _("display")

    content_panels = (
        BasePageWithRequiredIntro.content_panels
        + RequiredHeroImageMixin.content_panels
        + ContentWarningMixin.content_panels
        + [
            MultiFieldPanel(
                [
                    FieldPanel("body"),
                    FieldPanel("display_highlights_title"),
                    FieldPanel("display_highlights"),
                ],
                heading=_("Content"),
            ),
            MultiFieldPanel(
                [
                    FieldPanel("related_pages_title"),
                    FieldPanel("related_pages_description"),
                    FieldPanel("featured_page"),
                    FieldPanel("related_pages"),
                    FieldPanel("shop"),
                ],
                heading=_("Related content"),
            ),
        ]
    )

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
                FieldPanel("location"),
            ],
            heading=_("Location details"),
        ),
    ]

    promote_panels = BasePageWithRequiredIntro.promote_panels + [
        InlinePanel(
            "page_series_tags",
            heading=_("Series"),
            max_num=3,
        ),
    ]

    default_api_fields = BasePageWithRequiredIntro.default_api_fields + [
        APIField("start_date"),
        APIField("end_date"),
        APIField("price"),
        APIField("short_location"),
    ]

    api_fields = (
        BasePageWithRequiredIntro.api_fields
        + RequiredHeroImageMixin.api_fields
        + ContentWarningMixin.api_fields
        + [
            APIField("start_date"),
            APIField("end_date"),
            APIField("exclude_days"),
            APIField("price"),
            APIField("open_days"),
            APIField("booking_details", serializer=RichTextSerializer()),
            APIField("audience_heading"),
            APIField("audience_detail"),
            APIField("location", serializer=LocationSerializer()),
            APIField("body"),
            APIField("display_highlights_title"),
            APIField("display_highlights"),
            APIField("related_pages_title"),
            APIField("related_pages_description", serializer=RichTextSerializer()),
            APIField("featured_page", serializer=DefaultPageSerializer()),
            APIField("related_pages"),
            APIField("shop"),
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

    parent_page_types = [
        "whatson.ExhibitionsListingPage",
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


class ExhibitionPage(
    AccentColourMixin,
    HeroStyleMixin,
    HeroLayoutMixin,
    RequiredHeroImageMixin,
    ContentWarningMixin,
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

    location = models.ForeignKey(
        "core.Location",
        null=True,
        blank=False,
        on_delete=models.SET_NULL,
        related_name="+",
        verbose_name=_("location"),
        help_text=_("The location of the exhibition."),
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

    @cached_property
    def type_label(cls) -> str:
        """
        Overrides the type_label method from BasePage, to return the correct
        type label for the exhibition page.
        """
        if cls.end_date:
            if cls.end_date < timezone.now().date():
                return "Past exhibition"
        return "Exhibition"

    @cached_property
    def short_location(self) -> str:
        """
        Returns a short version of the location name.
        """
        if location := self.location:
            if location.online:
                return "Online"
            elif location.at_tna:
                return "At The National Archives, Kew"
            else:
                return location.address_line_1 or location.space_name or "In-person"

    class Meta:
        verbose_name = _("exhibition page")
        verbose_name_plural = _("exhibition pages")
        verbose_name_public = _("exhibition")

    content_panels = [
        TitleFieldPanel("title"),
        FieldPanel("subtitle"),
        FieldPanel("custom_warning_text"),
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
        FieldPanel("location"),
    ]

    design_panels = [
        FieldPanel("accent_colour"),
    ]

    promote_panels = BasePageWithRequiredIntro.promote_panels + [
        InlinePanel(
            "page_series_tags",
            heading=_("Series"),
            max_num=3,
        ),
    ]

    default_api_fields = BasePageWithRequiredIntro.default_api_fields + [
        APIField("start_date"),
        APIField("end_date"),
        APIField("price"),
        APIField("short_location"),
    ]

    api_fields = (
        BasePageWithRequiredIntro.api_fields
        + RequiredHeroImageMixin.api_fields
        + HeroStyleMixin.api_fields
        + HeroLayoutMixin.api_fields
        + AccentColourMixin.api_fields
        + ContentWarningMixin.api_fields
        + [
            APIField("short_location"),
            APIField("subtitle"),
            APIField("start_date"),
            APIField("end_date"),
            APIField("exclude_days"),
            APIField("price"),
            APIField("open_days"),
            APIField("booking_details", serializer=RichTextSerializer()),
            APIField("audience_heading"),
            APIField("audience_detail"),
            APIField("location", serializer=LocationSerializer()),
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
        ]
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

    parent_page_types = [
        "whatson.ExhibitionsListingPage",
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
