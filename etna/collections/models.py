from django.db import models
from django.utils.functional import cached_property

from modelcluster.fields import ParentalKey
from wagtail.admin.panels import FieldPanel, InlinePanel
from wagtail.fields import StreamField
from wagtail.images import get_image_model_string
from wagtail.models import Orderable

from wagtailmetadata.models import MetadataPageMixin

from etna.stories.models import StoriesPage

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
    ]


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

    featured_story = models.ForeignKey(
        "stories.StoriesPage", blank=True, null=True, on_delete=models.SET_NULL
    )

    body = StreamField(TopicExplorerPageStreamBlock, blank=True, use_json_field=True)

    content_panels = BasePage.content_panels + [
        FieldPanel("sub_heading"),
        FieldPanel("featured_story"),
        FieldPanel("body"),
    ]
    promote_panels = MetadataPageMixin.promote_panels + TeaserImageMixin.promote_panels
    settings_panels = BasePage.settings_panels + AlertMixin.settings_panels

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
    def related_stories(self):
        return (
            StoriesPage.objects.filter(topic=self)
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

    featured_story = models.ForeignKey(
        "stories.StoriesPage", blank=True, null=True, on_delete=models.SET_NULL
    )
    body = StreamField(
        TimePeriodExplorerPageStreamBlock, blank=True, use_json_field=True
    )
    start_year = models.IntegerField(blank=False)
    end_year = models.IntegerField(blank=False)
    content_panels = BasePage.content_panels + [
        FieldPanel("sub_heading"),
        FieldPanel("featured_story"),
        FieldPanel("body"),
        FieldPanel("start_year"),
        FieldPanel("end_year"),
    ]
    promote_panels = MetadataPageMixin.promote_panels + TeaserImageMixin.promote_panels
    settings_panels = BasePage.settings_panels + AlertMixin.settings_panels

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
    def related_stories(self):
        return (
            StoriesPage.objects.filter(time_period=self)
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
