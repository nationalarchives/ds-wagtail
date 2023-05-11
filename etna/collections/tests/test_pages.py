import unittest

from wagtail.test.utils import WagtailPageTestCase

from wagtail.models import PageViewRestriction, Site

from ..models import (
    ExplorerIndexPage,
    TimePeriodExplorerIndexPage,
    TimePeriodExplorerPage,
    TopicExplorerIndexPage,
    TopicExplorerPage,
    HighlightGalleryPage,
)


class TestPages(WagtailPageTestCase):
    def setUp(self):
        self.login()
        root_page = Site.objects.get().root_page

        self.explorer_index_page = ExplorerIndexPage(
            title="Explorer Page", intro="test", teaser_text="test"
        )
        root_page.add_child(instance=self.explorer_index_page)

        self.topic_explorer_index_page = TopicExplorerIndexPage(
            title="Topics", intro="topics", teaser_text="topic index"
        )
        self.explorer_index_page.add_child(instance=self.topic_explorer_index_page)

        self.topic_explorer_page = TopicExplorerPage(
            title="Test Topic",
            slug="topic",
            teaser_text="test",
            intro="test",
        )
        self.topic_explorer_index_page.add_child(instance=self.topic_explorer_page)

        self.time_period_explorer_index_page = TimePeriodExplorerIndexPage(
            title="Time Periods",
            intro="time periods",
            teaser_text="time period index",
        )
        self.explorer_index_page.add_child(instance=self.time_period_explorer_index_page)

        self.time_period_explorer_page = TimePeriodExplorerPage(
            title="Test Time Period",
            slug="time-period",
            teaser_text="test",
            intro="test",
            start_year=1000,
            end_year=2000,
        )
        self.time_period_explorer_index_page.add_child(instance=self.time_period_explorer_page)

        self.highlight_gallery_page = HighlightGalleryPage(
            title="Highlight Gallery",
            intro="test",
            teaser_text="test",
        )
        self.time_period_explorer_page.add_child(instance=self.highlight_gallery_page)

    def test_explorer_index_page(self):
        self.assertPageIsEditable(page=self.explorer_index_page)