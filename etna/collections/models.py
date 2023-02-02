from typing import List, Optional, Tuple, Union

from django.db import models
from django.utils.functional import cached_property
from django.utils.translation import gettext_lazy as _

from modelcluster.fields import ParentalKey
from wagtail.admin.panels import FieldPanel, InlinePanel
from wagtail.fields import StreamField
from wagtail.images import get_image_model_string
from wagtail.models import Orderable, Page

from wagtailmetadata.models import MetadataPageMixin

from ..alerts.models import AlertMixin
from ..ciim.exceptions import APIManagerException, KongAPIError
from ..core.models import BasePage
from ..records.models import Record
from ..records.widgets import RecordChooser
from ..teasers.models import TeaserImageMixin
from .blocks import (
    ExplorerIndexPageStreamBlock,
    TimePeriodExplorerIndexPageStreamBlock,
    TimePeriodExplorerPageStreamBlock,
    TopicExplorerIndexPageStreamBlock,
    TopicExplorerPageStreamBlock,
)


class ExplorerIndexPage(AlertMixin, TeaserImageMixin, MetadataPageMixin, BasePage):
    """Collection Explorer landing BasePage.

    This page is the starting point for a user's journey through the collection
    explorer.
    """

    sub_heading = models.CharField(max_length=200, blank=False)
    body = StreamField(ExplorerIndexPageStreamBlock, blank=True, use_json_field=True)

    content_panels = BasePage.content_panels + [
        FieldPanel("sub_heading"),
        FieldPanel("body"),
    ]
    promote_panels = MetadataPageMixin.promote_panels + TeaserImageMixin.promote_panels
    settings_panels = BasePage.settings_panels + AlertMixin.settings_panels

    parent_page_types = ["home.HomePage"]
    subpage_types = [
        "collections.TopicExplorerIndexPage",
        "collections.TimePeriodExplorerIndexPage",
        "articles.RecordArticlePage",
    ]

    # DataLayerMixin overrides
    gtm_content_group = "Explorer"


class TopicExplorerIndexPage(TeaserImageMixin, MetadataPageMixin, BasePage):
    """Topic explorer BasePage.

    This page lists all child TopicExplorerPages
    """

    sub_heading = models.CharField(max_length=200, blank=False)

    body = StreamField(
        TopicExplorerIndexPageStreamBlock, blank=True, use_json_field=True
    )

    content_panels = BasePage.content_panels + [
        FieldPanel("sub_heading"),
        FieldPanel("body"),
    ]
    promote_panels = MetadataPageMixin.promote_panels + TeaserImageMixin.promote_panels

    # DataLayerMixin overrides
    gtm_content_group = "Explorer"

    @cached_property
    def featured_pages(self):
        """Return a sample of child pages for rendering in teaser."""
        return (
            self.get_children()
            .type(TopicExplorerPage)
            .order_by("?")
            .live()
            .specific()[:3]
        )

    @cached_property
    def topic_explorer_pages(self):
        """Fetch all child TopicExplorerPages for display in list."""
        return (
            self.get_children()
            .type(TopicExplorerPage)
            .order_by("title")
            .live()
            .specific()
        )

    max_count = 1
    parent_page_types = ["collections.ExplorerIndexPage"]
    subpage_types = [
        "collections.TopicExplorerPage",
    ]


class TopicExplorerPage(AlertMixin, TeaserImageMixin, MetadataPageMixin, BasePage):
    """Topic explorer BasePage.

    This page represents one of the many categories a user may select in the
    collection explorer.

    A category page is responsible for listing its child pages, which may be either
    another CategoryPage (to allow the user to make a more fine-grained choice) or a
    single ResultsPage (to output the results of their selection).
    """

    sub_heading = models.CharField(max_length=200, blank=False)

    featured_article = models.ForeignKey(
        "articles.ArticlePage", blank=True, null=True, on_delete=models.SET_NULL
    )

    body = StreamField(TopicExplorerPageStreamBlock, blank=True, use_json_field=True)

    content_panels = BasePage.content_panels + [
        FieldPanel("sub_heading"),
        FieldPanel("featured_article", heading=_("Featured article")),
        FieldPanel("body"),
    ]
    promote_panels = MetadataPageMixin.promote_panels + TeaserImageMixin.promote_panels
    settings_panels = BasePage.settings_panels + AlertMixin.settings_panels

    # DataLayerMixin overrides
    gtm_content_group = "Explorer"

    @property
    def results_pages(self):
        """Fetch child results period pages for rendering on the front end."""
        return self.get_children().type(ResultsPage).order_by("title").live().specific()

    parent_page_types = [
        "collections.TopicExplorerIndexPage",
        "collections.TopicExplorerPage",
    ]
    subpage_types = ["collections.TopicExplorerPage", "collections.ResultsPage"]

    @cached_property
    def related_articles(self):
        from etna.articles.models import ArticlePage

        return (
            ArticlePage.objects.filter(topic=self)
            .live()
            .select_related("teaser_image")
            .order_by("title")[:3]
        )


class TimePeriodExplorerIndexPage(TeaserImageMixin, MetadataPageMixin, BasePage):
    """Time period explorer BasePage.

    This page lists all child TimePeriodExplorerPage
    """

    sub_heading = models.CharField(max_length=200, blank=False)

    body = StreamField(
        TimePeriodExplorerIndexPageStreamBlock, blank=True, use_json_field=True
    )

    content_panels = BasePage.content_panels + [
        FieldPanel("sub_heading"),
        FieldPanel("body"),
    ]
    promote_panels = MetadataPageMixin.promote_panels + TeaserImageMixin.promote_panels

    # DataLayerMixin overrides
    gtm_content_group = "Explorer"

    @cached_property
    def featured_pages(self):
        """Return a sample of child pages for rendering in teaser."""
        return (
            self.get_children()
            .type(TimePeriodExplorerPage)
            .order_by("?")
            .live()
            .specific()[:3]
        )

    @cached_property
    def time_period_explorer_pages(self):
        """Fetch all child TimePeriodExplorerPages for display in list."""
        return (
            self.get_children()
            .type(TimePeriodExplorerPage)
            .order_by("timeperiodexplorerpage__start_year")
            .live()
            .specific()
        )

    max_count = 1
    parent_page_types = ["collections.ExplorerIndexPage"]
    subpage_types = [
        "collections.TimePeriodExplorerPage",
    ]


class TimePeriodExplorerPage(AlertMixin, TeaserImageMixin, MetadataPageMixin, BasePage):
    """Time period BasePage.

    This page represents one of the many categories a user may select in the
    collection explorer.

    A category page is responsible for listing its child pages, which may be either
    another CategoryPage (to allow the user to make a more fine-grained choice) or a
    single ResultsPage (to output the results of their selection).
    """

    sub_heading = models.CharField(max_length=200, blank=False)

    featured_article = models.ForeignKey(
        "articles.ArticlePage", blank=True, null=True, on_delete=models.SET_NULL
    )
    body = StreamField(
        TimePeriodExplorerPageStreamBlock, blank=True, use_json_field=True
    )
    start_year = models.IntegerField(blank=False)
    end_year = models.IntegerField(blank=False)
    content_panels = BasePage.content_panels + [
        FieldPanel("sub_heading"),
        FieldPanel("featured_article", heading=_("Featured article")),
        FieldPanel("body"),
        FieldPanel("start_year"),
        FieldPanel("end_year"),
    ]
    promote_panels = MetadataPageMixin.promote_panels + TeaserImageMixin.promote_panels
    settings_panels = BasePage.settings_panels + AlertMixin.settings_panels

    # DataLayerMixin overrides
    gtm_content_group = "Explorer"

    @property
    def results_pages(self):
        """Fetch child results period pages for rendering on the front end."""
        return self.get_children().type(ResultsPage).order_by("title").live().specific()

    parent_page_types = [
        "collections.TimePeriodExplorerIndexPage",
        "collections.TimePeriodExplorerPage",
    ]
    subpage_types = ["collections.TimePeriodExplorerPage", "collections.ResultsPage"]

    @cached_property
    def related_articles(self):
        from etna.articles.models import ArticlePage

        return (
            ArticlePage.objects.filter(time_period=self)
            .live()
            .select_related("teaser_image")
            .order_by("title")[:3]
        )


class ResultsPage(AlertMixin, TeaserImageMixin, MetadataPageMixin, BasePage):
    """Results BasePage.

    This page is a placeholder for the results page at the end of a user's
    journey through the collection explorer.

    Eventually this page will run an editor-defined query against the
    collections API and display the results.
    """

    title_prefix = models.CharField(max_length=200, blank=True)
    sub_heading = models.CharField(max_length=200, blank=False)
    introduction = models.TextField(blank=False)

    content_panels = BasePage.content_panels + [
        FieldPanel("title_prefix"),
        FieldPanel("sub_heading"),
        FieldPanel("introduction"),
        InlinePanel("records", heading="Records"),
    ]
    promote_panels = MetadataPageMixin.promote_panels + TeaserImageMixin.promote_panels
    settings_panels = BasePage.settings_panels + AlertMixin.settings_panels

    parent_page_types = [
        "collections.TimePeriodExplorerPage",
        "collections.TopicExplorerPage",
    ]
    subpage_types = []

    # DataLayerMixin overrides
    gtm_content_group = "Explorer"


class ResultsPageRecord(Orderable, models.Model):
    """Map orderable records data to ResultsPage"""

    page = ParentalKey("ResultsPage", on_delete=models.CASCADE, related_name="records")
    record_iaid = models.TextField(verbose_name="Record")
    teaser_image = models.ForeignKey(
        get_image_model_string(),
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="+",
    )
    description = models.TextField(
        help_text="Optional field to override the description for this record in the teaser.",
        blank=True,
    )

    @cached_property
    def record(self):
        """Fetch associated record BasePage.

        Capture any exception thrown by KongClient and return None so we can
        skip this record on the results BasePage.
        """
        try:
            return Record.api.fetch(iaid=self.record_iaid)
        except (KongAPIError, APIManagerException):
            return None

    panels = [
        FieldPanel("record_iaid", widget=RecordChooser),
        FieldPanel("teaser_image"),
        FieldPanel("description"),
    ]


class PageTopic(Orderable):
    """
    This model allows any page type to be associated with one or more topics
    in a way that retains the order of topics selected.

    The ``sort_order`` field value from ``Orderable`` can be used to pull out
    the 'first' topic to treat as the 'primary topic' for a page, and can also
    used to prioritise items for a list of 'pages related to a topic'.

    Just add `InlinePanel("page_topics")` to a page type's panel
    configuration to use it!
    """

    page = ParentalKey(Page, on_delete=models.CASCADE, related_name="page_topics")
    topic = models.ForeignKey(
        TopicExplorerPage,
        verbose_name=_("topic"),
        related_name="topic_pages",
        on_delete=models.CASCADE,
    )


class PageTimePeriod(Orderable):
    """
    This model allows any page type to be associated with one or more topics
    in a way that retains the order of topics selected.

    The ``sort_order`` field value from ``Orderable`` can be used to pull out
    the 'first' topic to treat as the 'primary topic' for a page, and can also
    used to prioritise items for a list of 'pages related to a topic'.

    Just add `InlinePanel("page_time_periods")` to a page type's panel
    configuration to use it!
    """

    page = ParentalKey(Page, on_delete=models.CASCADE, related_name="page_time_periods")
    time_period = models.ForeignKey(
        TimePeriodExplorerPage,
        verbose_name=_("time period"),
        related_name="time_period_pages",
        on_delete=models.CASCADE,
    )


class TopicalPageMixin:
    """
    A mixin for pages that use the ``PageTopic`` and ``PageTimePeriod`` models
    in order to be associated with one or many topics/time periods. It simply
    adds a few properies to support robust, efficient access the related topic
    and time period pages.
    """

    @classmethod
    def get_time_periods_inlinepanel(
        cls, max_num: Optional[int] = 4, min_num: Optional[int] = None
    ) -> InlinePanel:
        return InlinePanel(
            "page_time_periods",
            heading=_("Related time periods"),
            min_num=min_num,
            max_num=max_num,
        )

    @classmethod
    def get_topics_inlinepanel(
        cls, max_num: Optional[int] = 4, min_num: Optional[int] = None
    ) -> InlinePanel:
        return InlinePanel(
            "page_topics",
            heading=_("Related topics"),
            min_num=min_num,
            max_num=max_num,
        )

    @cached_property
    def primary_topic(self) -> Union[TopicExplorerPage, None]:
        try:
            return self.topics[0]
        except IndexError:
            return None

    @cached_property
    def topics(self) -> Tuple[TopicExplorerPage]:
        return tuple(
            item.topic
            for item in self.page_topics.select_related("topic").filter(
                topic__live=True
            )
        )

    @cached_property
    def topics_alphabetical(self) -> List[TopicExplorerPage]:
        return sorted(self.topic, key=lambda item: item.title.lower())

    @property
    def topic_names(self) -> str:
        """
        Returns the titles of all related topics, joined together into one big
        comma-separated string. Ideal for indexing!
        """
        return ", ".join(item.title for item in self.topics)

    @cached_property
    def primary_time_period(self) -> Union[TimePeriodExplorerPage, None]:
        try:
            return self.time_periods[0]
        except IndexError:
            return None

    @cached_property
    def time_periods(self) -> Tuple[TimePeriodExplorerPage]:
        return tuple(
            item.time_period
            for item in self.page_time_periods.select_related("time_period").filter(
                time_period__live=True
            )
        )

    @cached_property
    def time_periods_chronological(self) -> List[TimePeriodExplorerPage]:
        return sorted(self.time_periods, key=lambda item: item.start_year)

    @property
    def time_period_names(self) -> str:
        """
        Returns the titles of all related time periods, joined together into
        one big comma-separated string. Ideal for indexing!
        """
        return ", ".join(item.title for item in self.time_periods)
