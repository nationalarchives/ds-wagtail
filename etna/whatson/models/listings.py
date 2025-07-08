import datetime

from django.db import models
from django.utils import timezone
from django.utils.functional import cached_property
from django.utils.translation import gettext_lazy as _
from modelcluster.fields import ParentalKey
from wagtail.admin.panels import (
    FieldPanel,
    InlinePanel,
    PageChooserPanel,
)
from wagtail.api import APIField
from wagtail.models import Page

from etna.core.models import (
    BasePageWithRequiredIntro,
)
from etna.core.serializers import (
    DefaultPageSerializer,
)

from ..serializers import (
    EventTypeSerializer,
)
from .details import (
    DisplayPage,
    EventPage,
    ExhibitionPage,
)


def get_specific_listings(
    page_types: list[Page] = [],
    filters: dict = {},
    order_by: str = "start_date",
    exclude: dict = {},
) -> list:
    """
    Helper function to get a list of specific pages based on the provided page types, filters, and order by criteria.

    This allows us to combine and compare different page types (like ExhibitionPage and DisplayPage) in a single query.

    Currently used for listing events and exhibitions in various listing pages.
    """
    pages = []

    for page_type in page_types:
        pages.extend(
            page_type.objects.exclude(**exclude)
            .filter(**filters)
            .live()
            .public()
            .distinct()
            .order_by(order_by)
        )

    return pages


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
        return get_specific_listings(
            page_types=[EventPage],
            filters={"pk__in": self.related_page_pks, "end_date__gte": timezone.now()},
            order_by="start_date",
        )

    @cached_property
    def exhibition_listings(self) -> list:
        """
        Returns a list of exhibition and display pages that belong to this series.
        """
        return get_specific_listings(
            page_types=[ExhibitionPage, DisplayPage],
            filters={"pk__in": self.related_page_pks, "end_date__gt": timezone.now()},
            order_by="start_date",
            exclude={"pk": self.featured_page_id},
        )

    @cached_property
    def latest_listings(self) -> list:
        """
        Returns a list of the latest event pages that belong to the categories
        selected for this category page.
        """
        return self.event_listings[:3]

    @cached_property
    def type_label(cls) -> str:
        return "What's On"

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

    class Meta:
        verbose_name = _("Series listing page")
        verbose_name_plural = _("Series listing pages")


class CategorySelection(models.Model):
    page = ParentalKey(
        "wagtailcore.Page",
        on_delete=models.CASCADE,
        related_name="category_pages",
    )
    category = models.ForeignKey(
        "whatson.EventType",
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
        return get_specific_listings(
            page_types=[EventPage],
            filters={
                "event_type__in": self.categories,
                "end_date__gte": timezone.now(),
            },
            order_by="start_date",
        )

    @cached_property
    def latest_listings(self) -> list:
        """
        Returns a list of the latest event pages that belong to the categories
        selected for this category page.
        """
        return self.event_listings[:3]

    @cached_property
    def type_label(cls) -> str:
        return "What's On"

    default_api_fields = BasePageWithRequiredIntro.default_api_fields + [
        APIField("latest_listings", serializer=DefaultPageSerializer(many=True)),
    ]

    api_fields = BasePageWithRequiredIntro.api_fields + [
        APIField("featured_page", serializer=DefaultPageSerializer()),
        APIField("categories", serializer=EventTypeSerializer(many=True)),
        APIField(
            "event_listings",
            serializer=DefaultPageSerializer(many=True),
        ),
    ]

    class Meta:
        verbose_name = _("Category listing page")
        verbose_name_plural = _("Category listing pages")


class WhatsOnLocationListingPage(BasePageWithRequiredIntro):
    """
    A page for listing events and exhibitions online or at TNA.
    """

    at_tna = models.BooleanField(
        default=False,
        verbose_name=_("at The National Archives"),
        help_text=_("Check this box to display events at The National Archives."),
    )

    online = models.BooleanField(
        default=False,
        verbose_name=_("online"),
        help_text=_("Check this box to display online events."),
    )

    @cached_property
    def type_label(cls) -> str:
        return "What's On"

    @cached_property
    def event_listings(self) -> list:
        """
        Returns a list of event pages that are happening at The National Archives or online.
        """
        return get_specific_listings(
            page_types=[EventPage],
            filters={
                "location__at_tna": self.at_tna,
                "location__online": self.online,
                "end_date__gte": timezone.now(),
            },
            order_by="start_date",
        )

    @cached_property
    def exhibition_listings(self) -> list:
        """
        Returns a list of exhibition and display pages that are happening at The National Archives or online.
        """
        return get_specific_listings(
            page_types=[ExhibitionPage, DisplayPage],
            filters={
                "location__at_tna": self.at_tna,
                "location__online": self.online,
                "end_date__gte": timezone.now(),
            },
            order_by="start_date",
        )

    content_panels = BasePageWithRequiredIntro.content_panels + [
        FieldPanel(
            "at_tna",
        ),
        FieldPanel(
            "online",
        ),
    ]

    api_fields = BasePageWithRequiredIntro.api_fields + [
        APIField("at_tna"),
        APIField("online"),
        APIField(
            "event_listings",
            serializer=DefaultPageSerializer(many=True),
        ),
        APIField(
            "exhibition_listings",
            serializer=DefaultPageSerializer(many=True),
        ),
    ]

    max_count = 2

    subpage_types = []

    parent_page_types = [
        "whatson.WhatsOnPage",
    ]

    class Meta:
        verbose_name = _("Location listing page")
        verbose_name_plural = _("Location listing pages")


class WhatsOnDateListingPage(BasePageWithRequiredIntro):
    """
    A page for listing events/exhibitions within a certain date.
    """

    days = models.PositiveIntegerField(
        default=1,
        verbose_name=_("number of days"),
        help_text=_("The number of days in the future to list events/exhibitions."),
    )

    @cached_property
    def event_listings(self) -> list:
        """
        Returns a list of event pages that are happening between today and the date in `days`
        amount of days.
        """
        return get_specific_listings(
            page_types=[EventPage],
            filters={
                "sessions__start__gte": timezone.now(),
                "sessions__start__lte": timezone.now()
                + datetime.timedelta(days=self.days-1),
            },
            order_by="start_date",
        )

    @cached_property
    def exhibition_listings(self) -> list:
        """
        Returns a list of exhibition and display pages that are happening between today and the date in `days`
        amount of days.
        """
        return get_specific_listings(
            page_types=[ExhibitionPage, DisplayPage],
            filters={
                "start_date__lte": timezone.now() + datetime.timedelta(days=self.days-1),
                "end_date__gte": timezone.now(),
            },
            order_by="start_date",
        )

    @cached_property
    def type_label(cls) -> str:
        return "What's On"

    content_panels = BasePageWithRequiredIntro.content_panels + [
        FieldPanel(
            "days",
        ),
    ]

    default_api_fields = BasePageWithRequiredIntro.default_api_fields + [
        APIField(
            "days"
        ),
    ]

    api_fields = BasePageWithRequiredIntro.api_fields + [
        APIField("days"),
        APIField(
            "event_listings",
            serializer=DefaultPageSerializer(many=True),
        ),
        APIField(
            "exhibition_listings",
            serializer=DefaultPageSerializer(many=True),
        ),
    ]

    subpage_types = []

    parent_page_types = [
        "whatson.WhatsOnPage",
    ]

    class Meta:
        verbose_name = _("Date listing page")
        verbose_name_plural = _("Date listing pages")


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
        return get_specific_listings(
            page_types=[EventPage],
            filters={"end_date__gte": timezone.now()},
            order_by="start_date",
        )

    @cached_property
    def latest_listings(self) -> list:
        """
        Returns a list of the latest event pages.
        """
        return self.event_listings[:3]

    @cached_property
    def type_label(cls) -> str:
        return "What's On"

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
        return get_specific_listings(
            page_types=[ExhibitionPage, DisplayPage],
            filters={"end_date__gte": timezone.now()},
            order_by="start_date",
        )

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
        return get_specific_listings(
            page_types=[ExhibitionPage, DisplayPage],
            filters={"end_date__lt": timezone.now()},
            order_by="start_date",
        )

    @cached_property
    def type_label(cls) -> str:
        return "What's On"

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
