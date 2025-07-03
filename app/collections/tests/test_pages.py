from wagtail.models import Site
from wagtail.test.utils import WagtailPageTestCase

from ..models import (
    ExplorerIndexPage,
    HighlightGalleryPage,
    TimePeriodExplorerIndexPage,
    TimePeriodExplorerPage,
    TopicExplorerIndexPage,
    TopicExplorerPage,
)


class TestPages(WagtailPageTestCase):
    @classmethod
    def setUpTestData(self):
        self.root_page = Site.objects.get().root_page

        self.explorer_index_page = ExplorerIndexPage(
            title="Explorer Page",
            intro="test",
            teaser_text="test",
        )
        self.root_page.add_child(instance=self.explorer_index_page)

        self.topic_explorer_index_page = TopicExplorerIndexPage(
            title="Topics",
            intro="topics",
            teaser_text="topic index",
        )
        self.explorer_index_page.add_child(instance=self.topic_explorer_index_page)

        self.topic_explorer_page1 = TopicExplorerPage(
            title="a Test Topic",
            slug="topic1",
            teaser_text="test",
            intro="test",
        )
        self.topic_explorer_index_page.add_child(instance=self.topic_explorer_page1)

        self.topic_explorer_page2 = TopicExplorerPage(
            title="b Test Topic",
            slug="topic2",
            teaser_text="test",
            intro="test",
        )
        self.topic_explorer_index_page.add_child(instance=self.topic_explorer_page2)

        self.topic_explorer_page3 = TopicExplorerPage(
            title="c Test Topic",
            slug="topic3",
            teaser_text="test",
            intro="test",
        )
        self.topic_explorer_index_page.add_child(instance=self.topic_explorer_page3)

        self.time_period_explorer_index_page = TimePeriodExplorerIndexPage(
            title="Time Periods",
            intro="time periods",
            teaser_text="time period index",
        )
        self.explorer_index_page.add_child(
            instance=self.time_period_explorer_index_page
        )

        self.time_period_explorer_page1 = TimePeriodExplorerPage(
            title="a Test Time Period",
            slug="time-period1",
            teaser_text="test",
            intro="test",
            start_year=1000,
            end_year=2000,
        )
        self.time_period_explorer_index_page.add_child(
            instance=self.time_period_explorer_page1
        )

        self.time_period_explorer_page2 = TimePeriodExplorerPage(
            title="b Test Time Period",
            slug="time-period2",
            teaser_text="test",
            intro="test",
            start_year=1000,
            end_year=2000,
        )
        self.time_period_explorer_index_page.add_child(
            instance=self.time_period_explorer_page2
        )

        self.time_period_explorer_page3 = TimePeriodExplorerPage(
            title="c Test Time Period",
            slug="time-period3",
            teaser_text="test",
            intro="test",
            start_year=1000,
            end_year=2000,
        )
        self.time_period_explorer_index_page.add_child(
            instance=self.time_period_explorer_page3
        )

        self.highlight_gallery_page = HighlightGalleryPage(
            title="Highlight Gallery",
            intro="test",
            teaser_text="test",
        )
        self.explorer_index_page.add_child(instance=self.highlight_gallery_page)

    def test_explorer_index_page(self):
        self.assertPageIsRenderable(self.explorer_index_page)

    def test_topic_explorer_index_page(self):
        self.assertPageIsRenderable(self.topic_explorer_index_page)

    def test_topic_explorer_page(self):
        self.assertPageIsRenderable(self.topic_explorer_page1)

    def test_time_period_explorer_index_page(self):
        self.assertPageIsRenderable(self.time_period_explorer_index_page)

    def test_time_period_explorer_page(self):
        self.assertPageIsRenderable(self.time_period_explorer_page1)

    def test_highlight_gallery_page(self):
        self.assertPageIsRenderable(self.highlight_gallery_page)

    def test_get_topic_featured_pages(self):
        featured_pages = self.topic_explorer_index_page.featured_pages
        self.assertEqual(len(featured_pages), 3)

    def test_check_topic_featured_pages(self):
        featured_pages = self.topic_explorer_index_page.featured_pages
        children = (
            self.topic_explorer_index_page.get_children().order_by("?").specific()
        )
        for page in featured_pages:
            self.assertIn(page, children)

    def test_get_time_featured_pages(self):
        featured_pages = self.time_period_explorer_index_page.featured_pages
        self.assertEqual(len(featured_pages), 3)

    def test_check_time_featured_pages(self):
        featured_pages = self.time_period_explorer_index_page.featured_pages
        children = (
            self.time_period_explorer_index_page.get_children().order_by("?").specific()
        )
        for page in featured_pages:
            self.assertIn(page, children)
