from django.core.exceptions import ObjectDoesNotExist
from django.db import models
from django.utils.functional import cached_property

from wagtail.admin.edit_handlers import FieldPanel, InlinePanel, StreamFieldPanel
from wagtail.core.fields import StreamField
from wagtail.core.models import Page, Orderable
from wagtail.images import get_image_model_string, get_image_model
from wagtail.images.edit_handlers import ImageChooserPanel

from modelcluster.fields import ParentalKey

from ..alerts.models import AlertMixin
from ..teasers.models import TeaserImageMixin
from ..records.models import RecordPage
from ..records.widgets import RecordChooser
from .blocks import (
    ExplorerIndexPageStreamBlock,
    TimePeriodExplorerPageStreamBlock,
    TimePeriodExplorerIndexPageStreamBlock,
    TopicExplorerPageStreamBlock,
    TopicExplorerIndexPageStreamBlock,
)


class ExplorerIndexPage(AlertMixin, TeaserImageMixin, Page):
    """Collection Explorer landing page.

    This page is the starting point for a user's journey through the collection
    explorer.
    """

    sub_heading = models.CharField(max_length=200, blank=False)
    body = StreamField(ExplorerIndexPageStreamBlock, blank=True)

    content_panels = Page.content_panels + [
        FieldPanel("sub_heading"),
        StreamFieldPanel("body"),
    ]
    promote_panels = Page.promote_panels + TeaserImageMixin.promote_panels
    settings_panels = Page.settings_panels + AlertMixin.settings_panels

    parent_page_types = ["home.HomePage"]
    subpage_types = [
        "collections.TopicExplorerIndexPage",
        "collections.TimePeriodExplorerIndexPage",
    ]


class TopicExplorerIndexPage(TeaserImageMixin, Page):
    """Topic explorer page.

    This page lists all child TopicExplorerPages
    """

    sub_heading = models.CharField(max_length=200, blank=False)
    body = StreamField(TopicExplorerIndexPageStreamBlock, blank=True)

    content_panels = Page.content_panels + [
        FieldPanel("sub_heading"),
        StreamFieldPanel("body"),
    ]
    promote_panels = Page.promote_panels + TeaserImageMixin.promote_panels

    @cached_property
    def featured_pages(self):
        """Return a sample of child pages for rendering in teaser."""
        return (
            self.get_children()
            .type(TopicExplorerPage)
            .order_by("?")
            .live()
            .public()
            .specific()[:3]
        )

    @cached_property
    def topic_explorer_pages(self):
        """Fetch all child public TopicExplorerPages for display in list."""
        return (
            self.get_children()
            .type(TopicExplorerPage)
            .order_by("title")
            .live()
            .public()
            .specific()
        )

    max_count = 1
    parent_page_types = ["collections.ExplorerIndexPage"]
    subpage_types = [
        "collections.TopicExplorerPage",
    ]


class TopicExplorerPage(AlertMixin, TeaserImageMixin, Page):
    """Topic explorer page.

    This page represents one of the many categories a user may select in the
    collection explorer.

    A category page is responsible for listing its child pages, which may be either
    another CategoryPage (to allow the user to make a more fine-grained choice) or a
    single ResultsPage (to output the results of their selection).
    """

    sub_heading = models.CharField(max_length=200, blank=False)

    body = StreamField(TopicExplorerPageStreamBlock, blank=True)

    content_panels = Page.content_panels + [
        FieldPanel("sub_heading"),
        StreamFieldPanel("body"),
    ]
    promote_panels = Page.promote_panels + TeaserImageMixin.promote_panels
    settings_panels = Page.settings_panels + AlertMixin.settings_panels

    @property
    def results_pages(self):
        """Fetch child results period pages for rendering on the front end."""
        return (
            self.get_children()
            .type(ResultsPage)
            .order_by("title")
            .live()
            .public()
            .specific()
        )

    parent_page_types = [
        "collections.TopicExplorerIndexPage",
        "collections.TopicExplorerPage",
    ]
    subpage_types = ["collections.TopicExplorerPage", "collections.ResultsPage"]


class TimePeriodExplorerIndexPage(TeaserImageMixin, Page):
    """Time period explorer page.

    This page lists all child TimePeriodExplorerPage
    """

    sub_heading = models.CharField(max_length=200, blank=False)
    body = StreamField(TimePeriodExplorerIndexPageStreamBlock, blank=True)

    content_panels = Page.content_panels + [
        FieldPanel("sub_heading"),
        StreamFieldPanel("body"),
    ]
    promote_panels = Page.promote_panels + TeaserImageMixin.promote_panels

    @cached_property
    def featured_pages(self):
        """Return a sample of child pages for rendering in teaser."""
        return (
            self.get_children()
            .type(TimePeriodExplorerPage)
            .order_by("?")
            .live()
            .public()
            .specific()[:3]
        )

    @cached_property
    def time_period_explorer_pages(self):
        """Fetch all child public TimePeriodExplorerPages for display in list."""
        return (
            self.get_children()
            .type(TimePeriodExplorerPage)
            .order_by("title")
            .live()
            .public()
            .specific()
        )

    max_count = 1
    parent_page_types = ["collections.ExplorerIndexPage"]
    subpage_types = [
        "collections.TimePeriodExplorerPage",
    ]


class TimePeriodExplorerPage(AlertMixin, TeaserImageMixin, Page):
    """Time period page.

    This page represents one of the many categories a user may select in the
    collection explorer.

    A category page is responsible for listing its child pages, which may be either
    another CategoryPage (to allow the user to make a more fine-grained choice) or a
    single ResultsPage (to output the results of their selection).
    """

    sub_heading = models.CharField(max_length=200, blank=False)
    body = StreamField(TimePeriodExplorerPageStreamBlock, blank=True)
    start_year = models.IntegerField(blank=False)
    end_year = models.IntegerField(blank=False)

    content_panels = Page.content_panels + [
        FieldPanel("sub_heading"),
        StreamFieldPanel("body"),
        FieldPanel("start_year"),
        FieldPanel("end_year"),
    ]
    promote_panels = Page.promote_panels + TeaserImageMixin.promote_panels
    settings_panels = Page.settings_panels + AlertMixin.settings_panels

    @property
    def results_pages(self):
        """Fetch child results period pages for rendering on the front end."""
        return (
            self.get_children()
            .type(ResultsPage)
            .order_by("title")
            .live()
            .public()
            .specific()
        )

    parent_page_types = [
        "collections.TimePeriodExplorerIndexPage",
        "collections.TimePeriodExplorerPage",
    ]
    subpage_types = ["collections.TimePeriodExplorerPage", "collections.ResultsPage"]


class ResultsPage(AlertMixin, TeaserImageMixin, Page):
    """Results page.

    This page is a placeholder for the results page at the end of a user's
    journey through the collection explorer.

    Eventually this page will run an editor-defined query against the
    collections API and display the results.
    """

    sub_heading = models.CharField(max_length=200, blank=False)
    introduction = models.TextField(blank=False)

    content_panels = Page.content_panels + [
        FieldPanel("sub_heading"),
        FieldPanel("introduction"),
        InlinePanel("records", heading="Records"),
    ]
    promote_panels = Page.promote_panels + TeaserImageMixin.promote_panels
    settings_panels = Page.settings_panels + AlertMixin.settings_panels

    max_count_per_parent = 1
    parent_page_types = []
    subpage_types = []


class ResultsPageRecordPage(Orderable, models.Model):
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
    def record_page(self):
        """Fetch associated record page"""
        return RecordPage.search.get(iaid=self.record_iaid)

    panels = [
        FieldPanel("record_iaid", widget=RecordChooser),
        ImageChooserPanel("teaser_image"),
        FieldPanel("description"),
    ]
